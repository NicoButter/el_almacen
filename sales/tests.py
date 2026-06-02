import json
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Cliente
from cuentas_corrientes.models import CuentaCorriente
from products.models import Product
from sales.models import DetalleVenta, LineItem, Ticket, Venta


class RealizarVentaTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.cashier = User.objects.create_user(
            username="cashier",
            password="pass",
            is_cashier=True,
        )
        self.client_user = User.objects.create_user(username="cliente", password="pass")
        self.cliente = Cliente.objects.create(user=self.client_user, nombre="Cliente Test")
        self.client.force_login(self.cashier)

    def post_sale(self, payload):
        return self.client.post(
            "/sales/api/realizar-venta/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_unit_sale_updates_stock_and_creates_sale_details(self):
        product = Product.objects.create(
            nombre="Yerba",
            descripcion="Paquete",
            costo=Decimal("100.00"),
            porcentaje_ganancia=Decimal("50.00"),
            cantidad_stock=Decimal("10.00"),
            unidad_medida="unidad",
        )

        response = self.post_sale({
            "cliente_id": self.cliente.pk,
            "productos": [{"id": product.pk, "cantidad": "3"}],
            "total": "450.00",
            "tipo_pago": "EFECTIVO",
        })

        self.assertEqual(response.status_code, 200)
        product.refresh_from_db()
        self.assertEqual(product.cantidad_stock, Decimal("7.00"))

        venta = Venta.objects.get()
        ticket = Ticket.objects.get()
        detalle = DetalleVenta.objects.get()
        line_item = LineItem.objects.get()

        self.assertEqual(venta.total, Decimal("450.00"))
        self.assertEqual(ticket.cliente, self.cliente)
        self.assertEqual(detalle.cantidad, Decimal("3.00"))
        self.assertEqual(detalle.total, Decimal("450.00"))
        self.assertEqual(line_item.quantity, Decimal("3.00"))
        self.assertEqual(line_item.subtotal, Decimal("450.00"))

    def test_fractional_sale_treats_quantity_as_grams_and_stock_as_kg(self):
        product = Product.objects.create(
            nombre="Queso",
            descripcion="Cremoso",
            costo=Decimal("1000.00"),
            porcentaje_ganancia=Decimal("20.00"),
            cantidad_stock=Decimal("2.00"),
            unidad_medida="kg",
            se_vende_fraccionado=True,
        )

        response = self.post_sale({
            "cliente_id": self.cliente.pk,
            "productos": [{"id": product.pk, "cantidad": "250"}],
            "total": "300.00",
            "tipo_pago": "EFECTIVO",
        })

        self.assertEqual(response.status_code, 200)
        product.refresh_from_db()
        self.assertEqual(product.cantidad_stock, Decimal("1.75"))
        self.assertEqual(Venta.objects.get().total, Decimal("300.00"))
        self.assertEqual(DetalleVenta.objects.get().total, Decimal("300.00"))
        self.assertEqual(LineItem.objects.get().subtotal, Decimal("300.00"))

    def test_insufficient_stock_does_not_create_partial_sale_or_discount_stock(self):
        product = Product.objects.create(
            nombre="Leche",
            descripcion="Entera",
            costo=Decimal("100.00"),
            porcentaje_ganancia=Decimal("0.00"),
            cantidad_stock=Decimal("1.00"),
            unidad_medida="unidad",
        )

        response = self.post_sale({
            "cliente_id": self.cliente.pk,
            "productos": [{"id": product.pk, "cantidad": "2"}],
            "total": "200.00",
            "tipo_pago": "EFECTIVO",
        })

        self.assertEqual(response.status_code, 400)
        product.refresh_from_db()
        self.assertEqual(product.cantidad_stock, Decimal("1.00"))
        self.assertEqual(Venta.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)
        self.assertEqual(LineItem.objects.count(), 0)
        self.assertEqual(DetalleVenta.objects.count(), 0)

    def test_current_account_sale_updates_balance(self):
        CuentaCorriente.objects.create(
            cliente=self.cliente,
            saldo=Decimal("10.00"),
            fecha_apertura=date.today(),
        )
        product = Product.objects.create(
            nombre="Pan",
            descripcion="Kg",
            costo=Decimal("100.00"),
            porcentaje_ganancia=Decimal("0.00"),
            cantidad_stock=Decimal("5.00"),
            unidad_medida="unidad",
        )

        response = self.post_sale({
            "cliente_id": self.cliente.pk,
            "productos": [{"id": product.pk, "cantidad": "2"}],
            "total": "200.00",
            "tipo_pago": "CUENTA_CORRIENTE",
        })

        self.assertEqual(response.status_code, 200)
        cuenta = self.cliente.cuenta_corriente_cc
        cuenta.refresh_from_db()
        self.assertEqual(cuenta.saldo, Decimal("210.00"))
        self.assertTrue(Venta.objects.get().es_fiada)
