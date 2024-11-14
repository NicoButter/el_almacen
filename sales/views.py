import io
import json
import weasyprint
import logging

from .models import Ticket

from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings

from .models import Ticket, Venta, DetalleVenta, LineItem, CuentaCorriente
from products.models import Product
from accounts.models import Cliente
from decimal import Decimal, InvalidOperation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------------------------------------------

def parse_decimal(value):
    # Elimina cualquier separador de miles (por ejemplo, coma)
    value = value.replace('.', '')  # Quitar los puntos de los miles
    value = value.replace(',', '.')  # Convertir coma en punto decimal
    return Decimal(value)

# ---------------------------------------------------------------------------------------------------------------

def ticket_list(request):
    tickets = Ticket.objects.all().order_by('-date') 
    return render(request, 'sales/ticket_list.html', {'tickets': tickets})

# ---------------------------------------------------------------------------------------------------------------

def reprint_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    line_items = ticket.line_items.all()
    return render(request, 'sales/reprint_ticket.html', {'ticket': ticket, 'line_items': line_items})

# ---------------------------------------------------------------------------------------------------------------

@login_required
def new_sale(request):
    if request.method == 'POST':
        try:
            # Intentar cargar los datos de la solicitud
            data = json.loads(request.body)
            cliente_id = data.get('cliente_id')
            productos_data = data.get('productos', [])
            venta_fiada = data.get('venta_fiada')

            # Log de inicio de procesamiento
            logger.info("Iniciando procesamiento de la nueva venta.")
            
            # Inicialización del total
            total_compra = Decimal('0.00')

            # Procesar cada producto
            for producto_data in productos_data:
                try:
                    producto_id = producto_data.get('id')
                    cantidad = Decimal(producto_data.get('cantidad'))
                    precio_unitario = Decimal(producto_data.get('precio_unitario'))
                    
                    # Validación y cálculo para productos fraccionados
                    producto = Product.objects.get(id=producto_id)
                    if producto.se_vende_fraccionado:
                        total_producto = precio_unitario * (cantidad / 1000)
                    else:
                        total_producto = precio_unitario * cantidad
                    
                    total_compra += total_producto
                except Exception as e:
                    logger.error(f"Error procesando el producto {producto_data.get('id')}: {str(e)}")
                    raise

            # Crear y guardar la venta
            venta = Venta(cliente_id=cliente_id, total=total_compra, fecha_venta=timezone.now())
            venta.save()

            # Agregar detalles de la venta
            for producto_data in productos_data:
                try:
                    producto_id = producto_data.get('id')
                    cantidad = Decimal(producto_data.get('cantidad'))
                    precio_unitario = Decimal(producto_data.get('precio_unitario'))
                    total_producto = precio_unitario * cantidad if not producto.se_vende_fraccionado else precio_unitario * (cantidad / 1000)
                    
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto_id=producto_id,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        total=total_producto
                    )
                except Exception as e:
                    logger.error(f"Error creando detalle de venta para producto {producto_data.get('id')}: {str(e)}")
                    raise

            # Verificar si es venta fiada y actualizar cuenta corriente
            if venta_fiada:
                venta.realizar_venta_fiada()
            
            logger.info(f"Venta procesada con éxito. ID de venta: {venta.id}")

            return JsonResponse({'success': True, 'ticket_id': venta.id})

        except (ValueError, TypeError, InvalidOperation) as e:
            logger.error(f"Error en la solicitud de venta: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error en la solicitud: {str(e)}'}, status=400)
        except Product.DoesNotExist:
            logger.error("Producto no encontrado durante la venta.")
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=404)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    productos = Product.objects.all()
    clientes = Cliente.objects.all()
    return render(request, 'sales/new_sale.html', {'productos': productos, 'clientes': clientes})

# ---------------------------------------------------------------------------------------------------------------

def buscar_venta(request):
    # lógica para buscar venta
    return render(request, 'sales/buscar_venta.html')

# ---------------------------------------------------------------------------------------------------------------

def get_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        data = {
            "nombre": product.nombre,
            "precio_venta": str(product.precio_venta),
            "se_vende_fraccionado": product.se_vende_fraccionado
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)
    
# ---------------------------------------------------------------------------------------------------------------

# Nueva vista para ProductDetailView
def product_detail(request, product_id):
    return get_product(request, product_id)

# ---------------------------------------------------------------------------------------------------------------

@login_required
def ticket_detail(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    line_items = LineItem.objects.filter(ticket=ticket)
    print("Line items in ticket detail:", line_items)


    return render(request, 'sales/ticket_detail.html', {
        'ticket': ticket,
        'line_items': line_items
    })

# ---------------------------------------------------------------------------------------------------------------

@csrf_exempt
@login_required
def realizar_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug(f"Datos recibidos: {data}")
            
            cliente_id = data.get('cliente_id')
            productos_data = data.get('productos', [])
            total_compra = data.get('total', 0)

            if not cliente_id or not productos_data or total_compra is None:
                logger.warning("Faltan datos de cliente, productos o total.")
                return JsonResponse({"success": False, "message": "Faltan datos de cliente, productos o total."}, status=400)

            cliente = get_object_or_404(Cliente, id=cliente_id)
            
            # Verificar si el cliente tiene cuenta corriente
            try:
                cuenta_corriente = CuentaCorriente.objects.get(cliente=cliente)
            except CuentaCorriente.DoesNotExist:
                logger.error(f"Cliente con ID {cliente.id} no tiene cuenta corriente.")
                return JsonResponse({
                    "success": False,
                    "message": "El cliente no tiene una cuenta corriente asociada."
                }, status=400)
            
            # Crear la venta
            logger.debug(f"Creando venta para el cliente {cliente.nombre} (ID: {cliente.id})")
            venta = Venta.objects.create(cliente=cliente, fecha_venta=timezone.now(), total=total_compra, cuenta_corriente=cuenta_corriente)

            # Llamar al método para agregar el monto de la venta a la cuenta corriente
            logger.debug(f"Realizando venta fiada para la venta {venta.id}")
            venta.realizar_venta_fiada()

            # Procesar productos de la venta (detalles de la venta)
            for item in productos_data:
                product_id = item.get('id')
                cantidad = Decimal(item.get('cantidad'))
                total_producto = Decimal(item.get('total'))
                precio_unitario = Decimal(item.get('precio_unitario'))

                product = get_object_or_404(Product, id=product_id)
                logger.debug(f"Procesando producto: {product.nombre}, cantidad: {cantidad}, precio unitario: {precio_unitario}")

                if product.se_vende_fraccionado:
                    cantidad_kg = cantidad / Decimal('1000')
                    if product.cantidad_stock < cantidad_kg:
                        logger.warning(f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} kg")
                        return JsonResponse({
                            "success": False,
                            "message": f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} kg"
                        }, status=400)
                    product.cantidad_stock -= cantidad_kg
                else:
                    if product.cantidad_stock < cantidad:
                        logger.warning(f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} unidades")
                        return JsonResponse({
                            "success": False,
                            "message": f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} unidades"
                        }, status=400)
                    product.cantidad_stock -= cantidad

                product.save()

                # Crear los detalles de la venta
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=product,
                    cantidad=cantidad,
                    total=total_producto,
                    precio_unitario=precio_unitario
                )
                logger.debug(f"Detalle de venta creado para el producto '{product.nombre}'")

            logger.info(f"Venta procesada correctamente, ID de ticket: {venta.id}")
            return JsonResponse({
                "success": True,
                "message": "Venta procesada correctamente",
                "ticket_id": venta.id
            })

        except Exception as e:
            logger.error(f"Error al procesar la venta: {e}")
            return JsonResponse({"success": False, "message": "Hubo un error al procesar la venta. Inténtalo nuevamente."}, status=500)


# ---------------------------------------------------------------------------------------------------------------

def enviar_ticket_email(request, ticket_id):
    # Obtener el ticket de la base de datos
    ticket = get_object_or_404(Ticket, id=ticket_id)
    line_items = ticket.line_items.all()

    # Renderizar el template a HTML
    html = render_to_string('ticket_details.html', {'ticket': ticket, 'line_items': line_items})

    # Convertir el HTML a PDF
    pdf = weasyprint.HTML(string=html).write_pdf()

    # Crear un archivo en memoria con el PDF
    pdf_file = io.BytesIO(pdf)

    # Crear el correo electrónico
    email = EmailMessage(
        'Detalles de tu Ticket de Compra',  # Asunto
        'Adjunto encontrarás el PDF con los detalles de tu compra.',  # Cuerpo del correo
        'from@example.com',  # Dirección de envío
        [ticket.cliente.email]  # Dirección de destino (cliente)
    )
    email.attach(f'ticket_{ticket.id}.pdf', pdf_file.getvalue(), 'application/pdf')

    # Enviar el correo
    email.send()

    # Redirigir a la página de confirmación o dashboard
    return HttpResponse('El ticket ha sido enviado por email.', content_type='text/plain')

# ---------------------------------------------------------------------------------------------------------------

def generar_pdf(request, ticket_id):
    # Obtener el ticket de la base de datos
    ticket = get_object_or_404(Ticket, id=ticket_id)
    line_items = ticket.line_items.all()

    # Renderizar el template a HTML
    html = render_to_string('ticket_details.html', {'ticket': ticket, 'line_items': line_items})

    # Convertir el HTML a PDF
    pdf = weasyprint.HTML(string=html).write_pdf()

    # Crear una respuesta HTTP con el PDF como adjunto
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'
    return response

# ---------------------------------------------------------------------------------------------------------------

def generar_pdf_whatsapp(request, ticket_id):
    # Obtener el ticket
    ticket = get_object_or_404(Ticket, id=ticket_id)
    line_items = ticket.line_items.all()

    # Renderizar el template a HTML
    html = render_to_string('ticket_details.html', {'ticket': ticket, 'line_items': line_items})

    # Convertir el HTML a PDF
    pdf = weasyprint.HTML(string=html).write_pdf()

    # Crear una respuesta con el archivo PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'
    return response

# ---------------------------------------------------------------------------------------------------------------