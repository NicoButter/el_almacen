# Generated by Django 5.1.2 on 2024-11-08 18:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_remove_cliente_direccion_remove_cliente_telefono_and_more"),
        ("products", "0004_rename_precio_product_costo_and_more"),
        ("sales", "0003_delete_cuentacorriente"),
    ]

    operations = [
        migrations.CreateModel(
            name="DetalleVenta",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cantidad", models.PositiveIntegerField()),
                (
                    "precio_unitario",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "producto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Venta",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fecha_venta", models.DateTimeField(auto_now_add=True)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.cliente",
                    ),
                ),
                (
                    "productos",
                    models.ManyToManyField(
                        through="sales.DetalleVenta", to="products.product"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="detalleventa",
            name="venta",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="sales.venta"
            ),
        ),
    ]
