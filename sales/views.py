import io
import json
import weasyprint
import logging

from django.db.models import Q, Sum
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.db import transaction

from .models import Ticket, Venta, DetalleVenta, LineItem, Pago
from products.models import Product
from accounts.models import Cliente
from cuentas_corrientes.models import CuentaCorriente

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

    # Calcular métricas
    total_tickets = Ticket.objects.count()
    total_ventas = Ticket.objects.aggregate(total=Sum('total'))['total'] or 0
    tickets_hoy = Ticket.objects.filter(date__date=timezone.now().date()).count()
    promedio_ticket = total_ventas / total_tickets if total_tickets > 0 else 0

    return render(request, 'sales/ticket_list.html', {
        'page_title': 'Lista de Tickets',
        'tickets': tickets,
        'total_tickets': total_tickets,
        'total_ventas': total_ventas,
        'tickets_hoy': tickets_hoy,
        'promedio_ticket': promedio_ticket,
    })

# ---------------------------------------------------------------------------------------------------------------

def reprint_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    line_items = ticket.line_items.all()
    return render(request, 'sales/reprint_ticket.html', {
        'page_title': 'Reimprimir Ticket',
        'ticket': ticket,
        'line_items': line_items
    })

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
            venta = Venta(cliente_id=cliente_id, total=total_compra, fecha_venta=timezone.now(), es_fiada=venta_fiada)
            venta.save()

            # Agregar detalles de la venta
            for producto_data in productos_data:
                try:
                    producto_id = producto_data.get('id')
                    cantidad = Decimal(producto_data.get('cantidad'))
                    precio_unitario = Decimal(producto_data.get('precio_unitario'))
                    
                    # Obtener el producto para verificar si se vende fraccionado
                    producto = Product.objects.get(id=producto_id)
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

            logger.info(f"Venta procesada con éxito. ID de venta: {venta.pk}")

            return JsonResponse({'success': True, 'ticket_id': venta.pk})

        except (ValueError, TypeError, InvalidOperation) as e:
            logger.error(f"Error en la solicitud de venta: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error en la solicitud: {str(e)}'}, status=400)
        except Product.DoesNotExist:
            logger.error("Producto no encontrado durante la venta.")
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=404)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    # Si es un GET request, renderiza el formulario
    productos = Product.objects.all()
    clientes = Cliente.objects.all()
    return render(request, 'sales/new_sale.html', {
        'page_title': 'Nueva Venta',
        'productos': productos,
        'clientes': clientes
    })

# ---------------------------------------------------------------------------------------------------------------

def buscar_venta(request):
    query = Venta.objects.all()

    # Obtener parámetros de búsqueda
    search = request.GET.get('search', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    ticket = request.GET.get('ticket', '').strip()
    monto_min = request.GET.get('monto_min')
    monto_max = request.GET.get('monto_max')
    estado = request.GET.get('estado', '').strip()

    # Filtrar por cliente o ID de venta
    if search:
        query = query.filter(
            Q(id__icontains=search) |
            Q(cliente__nombre__icontains=search)
        )

    # Filtrar por rango de fechas
    if fecha_inicio:
        query = query.filter(fecha_venta__gte=fecha_inicio)
    if fecha_fin:
        query = query.filter(fecha_venta__lte=fecha_fin)

    # Filtrar por número de ticket
    if ticket:
        query = query.filter(tickets__id__icontains=ticket)  # Se usa 'tickets__id' para acceder al ID de un ticket relacionado

    # Filtrar por rango de montos
    if monto_min:
        query = query.filter(total__gte=monto_min)
    if monto_max:
        query = query.filter(total__lte=monto_max)

    # Filtrar por estado
    if estado:
        if estado == 'pagada':
            query = query.filter(es_fiada=False)
        elif estado == 'fiada':
            query = query.filter(es_fiada=True)

    # Paginación
    page_number = request.GET.get('page', 1)  # Página actual
    per_page = int(request.GET.get('per_page', 10))  # Número de resultados por página (default: 10)
    paginator = Paginator(query, per_page)
    page_obj = paginator.get_page(page_number)

    return render(request, 'sales/buscar_venta.html', {
        'page_title': 'Buscar Ventas',
        'ventas': page_obj.object_list,
        'page_obj': page_obj,
        'per_page': per_page
    })

# ---------------------------------------------------------------------------------------------------------------

def get_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        data = {
            "nombre": product.nombre,
            "precio_venta": str(product.precio_venta),
            "se_vende_fraccionado": product.se_vende_fraccionado,
            "imagen": product.imagen.url
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

    # Acceder al objeto Venta relacionado con el Ticket
    venta = ticket.venta

    return render(request, 'sales/ticket_detail.html', {
        'page_title': 'Detalle del Ticket',
        'ticket': ticket,
        'line_items': line_items,
        'venta': venta  # Pasamos la venta para acceder a 'es_fiada'
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
            tipo_pago = data.get('tipo_pago')  # Tipo de pago recibido en la solicitud

            if not cliente_id or not productos_data or total_compra is None or not tipo_pago:
                logger.warning("Faltan datos de cliente, productos, total o tipo de pago.")
                return JsonResponse({"success": False, "message": "Faltan datos de cliente, productos, total o tipo de pago."}, status=400)

            # Asegurarse de que total_compra es un número
            try:
                total_compra = float(total_compra)
            except ValueError:
                logger.error("El campo 'total' debe ser un número.")
                return JsonResponse({
                    "success": False,
                    "message": "El campo 'total' debe ser un número válido."
                }, status=400)

            # Validación del tipo de pago
            tipo_pago_choices = ['EFECTIVO', 'TARJETA', 'CUENTA_CORRIENTE', 'QR', 'CREDITO', 'DEBITO']
            if tipo_pago not in tipo_pago_choices:
                logger.error(f"Tipo de pago '{tipo_pago}' no es válido.")
                return JsonResponse({
                    "success": False,
                    "message": f"El tipo de pago '{tipo_pago}' no es válido."
                }, status=400)

            cliente = get_object_or_404(Cliente, id=cliente_id)
            
            # Verificar si el cliente tiene cuenta corriente
            cuenta_corriente = getattr(cliente, 'cuenta_corriente_cc', None)
            es_fiada = False
            if tipo_pago == 'CUENTA_CORRIENTE':
                # Verificar si la venta es fiada
                if not cuenta_corriente:
                    logger.warning(f"El cliente con ID {cliente.pk} no tiene cuenta corriente.")
                    return JsonResponse({
                        "success": False,
                        "message": f"El cliente '{cliente.nombre}' no tiene cuenta corriente asociada. No se puede realizar la venta fiada."
                    }, status=400)
                es_fiada = True
            
            # Iniciar transacción para asegurar consistencia
            with transaction.atomic():
                # Crear la venta
                logger.debug(f"Creando venta para el cliente {cliente.nombre} (ID: {cliente.pk})")

                venta = Venta.objects.create(
                    cliente=cliente,
                    fecha_venta=timezone.now(),
                    total=total_compra,
                    cuenta_corriente=cuenta_corriente if es_fiada else None,
                    es_fiada=es_fiada,  # Se asigna el valor de es_fiada en la venta
                    tipo_de_pago=tipo_pago  # Asignamos el tipo de pago recibido
                )

                # Crear el ticket asociado a la venta
                ticket = Ticket.objects.create(
                    venta=venta,
                    total=total_compra,
                    cashier_id=request.user.id
                )

                logger.debug(f"Ticket creado para la venta ID: {venta.pk}, Ticket ID: {ticket.pk}")

                # Procesar productos de la venta (detalles de la venta)
                for item in productos_data:
                    product_id = item.get('id')
                    quantity = item.get('cantidad')  # Asegúrate de que la cantidad es un número entero
                    product = get_object_or_404(Product, id=product_id)
                    
                    logger.debug(f"Procesando producto: {product.nombre}, cantidad: {quantity}")

                    quantity = Decimal(str(quantity))

                    # Validación y cálculo para productos fraccionados
                    if product.se_vende_fraccionado:
                        cantidad_kg = quantity / Decimal('1000')
                        if product.cantidad_stock < cantidad_kg:
                            logger.warning(f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} kg")
                            return JsonResponse({
                                "success": False,
                                "message": f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} kg"
                            }, status=400)
                        product.cantidad_stock -= cantidad_kg
                    else:
                        if product.cantidad_stock < quantity:
                            logger.warning(f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} unidades")
                            return JsonResponse({
                                "success": False,
                                "message": f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} unidades"
                            }, status=400)
                        product.cantidad_stock -= quantity

                    product.save()

                    # Crear el LineItem (detalle de la venta)
                    LineItem.objects.create(
                        ticket=ticket,
                        product=product,
                        quantity=quantity,
                    )
                    logger.debug(f"Detalle de venta creado para el producto '{product.nombre}'")

                # Si la venta es fiada, actualizar el saldo de la cuenta corriente
                if es_fiada:
                    # Asegurarse de que total_compra es un Decimal
                    total_compra_decimal = Decimal(str(total_compra))
                    
                    # Verificar que cuenta_corriente existe (debería existir si es_fiada=True)
                    if cuenta_corriente is None:
                        logger.error("Error interno: venta marcada como fiada pero sin cuenta corriente")
                        raise ValueError("Cuenta corriente requerida para venta fiada")
                    
                    # Actualizamos el saldo de la cuenta corriente
                    cuenta_corriente.saldo += total_compra_decimal
                    cuenta_corriente.save()

                    logger.debug(f"Saldo actualizado de la cuenta corriente para el cliente '{cliente.nombre}': {cuenta_corriente.saldo}")

                # Crear el pago asociado al ticket (si es necesario)
                pago = Pago.objects.create(ticket=ticket, cliente=cliente, monto=total_compra)

                logger.debug(f"Pago registrado para el ticket ID: {ticket.pk}, Monto: {pago.monto}")

                # Confirmar la venta
                logger.info(f"Venta procesada correctamente, Ticket ID: {ticket.pk}")
                return JsonResponse({
                    "success": True,
                    "message": "Venta procesada correctamente",
                    "ticket_id": ticket.pk
                })

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error al procesar la venta: {e}")
            logger.debug(f"Detalles del error:\n{error_details}")
            return JsonResponse({
                "success": False,
                "message": "Hubo un error al procesar la venta. Inténtalo nuevamente.",
                "error": str(e),
                "traceback": error_details
            }, status=500)
    
    else:
        # Método HTTP no soportado
        return JsonResponse({
            "success": False,
            "message": "Método HTTP no permitido. Use POST."
        }, status=405)





# @csrf_exempt
# @login_required
# def realizar_venta(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             logger.debug(f"Datos recibidos: {data}")
            
#             cliente_id = data.get('cliente_id')
#             productos_data = data.get('productos', [])
#             total_compra = data.get('total', 0)

#             if not cliente_id or not productos_data or total_compra is None:
#                 logger.warning("Faltan datos de cliente, productos o total.")
#                 return JsonResponse({"success": False, "message": "Faltan datos de cliente, productos o total."}, status=400)

#             # Asegurarse de que total_compra es un número
#             try:
#                 total_compra = float(total_compra)
#             except ValueError:
#                 logger.error("El campo 'total' debe ser un número.")
#                 return JsonResponse({
#                     "success": False,
#                     "message": "El campo 'total' debe ser un número válido."
#                 }, status=400)

#             cliente = get_object_or_404(Cliente, id=cliente_id)
            
#             # Verificar si el cliente tiene cuenta corriente
#             cuenta_corriente = getattr(cliente, 'cuenta_corriente_cc', None)
#             if not cuenta_corriente:
#                 logger.warning(f"El cliente con ID {cliente.id} no tiene cuenta corriente.")
#                 return JsonResponse({
#                     "success": False,
#                     "message": f"El cliente '{cliente.nombre}' no tiene cuenta corriente asociada. No se puede realizar la venta fiada."
#                 }, status=400)
            
#             # Iniciar transacción para asegurar consistencia
#             with transaction.atomic():
#                 # Crear la venta
#                 logger.debug(f"Creando venta para el cliente {cliente.nombre} (ID: {cliente.id})")

#                 # Calcular si la venta es fiada (si hay cuenta corriente y el total es mayor a 0)
#                 es_fiada = cuenta_corriente and total_compra > 0

#                 venta = Venta.objects.create(
#                     cliente=cliente,
#                     fecha_venta=timezone.now(),
#                     total=total_compra,
#                     cuenta_corriente=cuenta_corriente,
#                     es_fiada=es_fiada,  # Se asigna el valor de es_fiada en la venta
#                     tipo_de_pago='CUENTA_CORRIENTE' if es_fiada else 'EFECTIVO'  # O 'TARJETA' si aplica
#                 )

#                 # Crear el ticket asociado a la venta
#                 ticket = Ticket.objects.create(
#                     venta=venta,
#                     total=total_compra,
#                     cashier_id=request.user.id
#                 )

#                 logger.debug(f"Ticket creado para la venta ID: {venta.id}, Ticket ID: {ticket.id}")

#                 # Procesar productos de la venta (detalles de la venta)
#                 for item in productos_data:
#                     product_id = item.get('id')
#                     quantity = item.get('cantidad')  # Asegúrate de que la cantidad es un número entero
#                     product = get_object_or_404(Product, id=product_id)
                    
#                     logger.debug(f"Procesando producto: {product.nombre}, cantidad: {quantity}")

#                     quantity = Decimal(str(quantity))

#                     # Validación y cálculo para productos fraccionados
#                     if product.se_vende_fraccionado:
#                         cantidad_kg = quantity / Decimal('1000')
#                         if product.cantidad_stock < cantidad_kg:
#                             logger.warning(f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} kg")
#                             return JsonResponse({
#                                 "success": False,
#                                 "message": f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} kg"
#                             }, status=400)
#                         product.cantidad_stock -= cantidad_kg
#                     else:
#                         if product.cantidad_stock < quantity:
#                             logger.warning(f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} unidades")
#                             return JsonResponse({
#                                 "success": False,
#                                 "message": f"No hay suficiente stock para el producto '{product.nombre}'. Disponible: {product.cantidad_stock} unidades"
#                             }, status=400)
#                         product.cantidad_stock -= quantity

#                     product.save()

#                     # Crear el LineItem (detalle de la venta)
#                     LineItem.objects.create(
#                         ticket=ticket,
#                         product=product,
#                         quantity=quantity,
#                     )
#                     logger.debug(f"Detalle de venta creado para el producto '{product.nombre}'")

#                 # Si la venta es fiada, actualizar el saldo de la cuenta corriente
#                 if es_fiada:
#                     # Asegurarse de que total_compra es un Decimal
#                     total_compra_decimal = Decimal(str(total_compra))
                    
#                     # Actualizamos el saldo de la cuenta corriente
#                     cuenta_corriente.saldo += total_compra_decimal
#                     cuenta_corriente.save()

#                     logger.debug(f"Saldo actualizado de la cuenta corriente para el cliente '{cliente.nombre}': {cuenta_corriente.saldo}")

#                 # Crear el pago asociado al ticket (si es necesario)
#                 pago = Pago.objects.create(ticket=ticket, cliente=cliente, monto=total_compra)

#                 logger.debug(f"Pago registrado para el ticket ID: {ticket.id}, Monto: {pago.monto}")

#                 # Confirmar la venta
#                 logger.info(f"Venta procesada correctamente, Ticket ID: {ticket.id}")
#                 return JsonResponse({
#                     "success": True,
#                     "message": "Venta procesada correctamente",
#                     "ticket_id": ticket.id
#                 })

#         except Exception as e:
#             import traceback
#             error_details = traceback.format_exc()
#             logger.error(f"Error al procesar la venta: {e}")
#             logger.debug(f"Detalles del error:\n{error_details}")
#             return JsonResponse({
#                 "success": False,
#                 "message": "Hubo un error al procesar la venta. Inténtalo nuevamente.",
#                 "error": str(e),
#                 "traceback": error_details
#             }, status=500)

# ---------------------------------------------------------------------------------------------------------------

def enviar_ticket_email(request, ticket_id):
    # Obtener el ticket de la base de datos
    ticket = get_object_or_404(Ticket, id=ticket_id)
    line_items = ticket.line_items.all()

    # Renderizar el template a HTML
    html = render_to_string('ticket_details.html', {'ticket': ticket, 'line_items': line_items})

    # Convertir el HTML a PDF
    pdf = weasyprint.HTML(string=html).write_pdf()
    
    # Verificar que el PDF se generó correctamente
    if pdf is None:
        logger.error(f"Error al generar PDF para el ticket {ticket_id}")
        return HttpResponse("Error al generar el PDF del ticket", status=500)

    # Crear un archivo en memoria con el PDF
    pdf_file = io.BytesIO(pdf)

    # Verificar que el ticket tiene un cliente asociado
    if ticket.cliente is None:
        logger.error(f"El ticket {ticket_id} no tiene un cliente asociado")
        return HttpResponse("El ticket no tiene un cliente asociado", status=400)

    # Crear el correo electrónico
    email = EmailMessage(
        'Detalles de tu Ticket de Compra',  # Asunto
        'Adjunto encontrarás el PDF con los detalles de tu compra.',  # Cuerpo del correo
        'from@example.com',  # Dirección de envío
        [ticket.cliente.user.email]  # Dirección de destino (cliente)
    )
    email.attach(f'ticket_{ticket.pk}.pdf', pdf_file.getvalue(), 'application/pdf')

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
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.pk}.pdf"'
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
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.pk}.pdf"'
    return response

# ---------------------------------------------------------------------------------------------------------------

def search_products(request):
    query = request.GET.get('query', '').strip()  # Eliminar espacios al principio y al final

    if query:  # Si hay un término de búsqueda
        # Filtrar los productos que contienen el texto de la búsqueda (sin importar mayúsculas/minúsculas)
        products = Product.objects.filter(nombre__icontains=query)
    else:
        products = Product.objects.none()  # Si no hay consulta, no devolver productos

    # Imprimir cantidad de productos encontrados
    print(f"Productos encontrados: {products.count()}")  # Esto te ayudará a ver si se encuentran productos

    # Formatear los productos para devolverlos como JSON
    products_data = []
    for product in products:
        products_data.append({
            'id': product.pk,
            'nombre': product.nombre,  # Cambiado de 'name' a 'nombre'
            'precio_venta': product.precio_venta,
        })
    
    return JsonResponse({'products': products_data})