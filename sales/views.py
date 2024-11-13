import io
import json
import weasyprint

from .models import Ticket

from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings



from .models import Ticket, Venta, DetalleVenta, LineItem
from products.models import Product
from accounts.models import Cliente

from decimal import Decimal

def parse_decimal(value):
    # Elimina cualquier separador de miles (por ejemplo, coma)
    value = value.replace('.', '')  # Quitar los puntos de los miles
    value = value.replace(',', '.')  # Convertir coma en punto decimal
    return Decimal(value)


def ticket_list(request):
    tickets = Ticket.objects.all().order_by('-date') 
    return render(request, 'sales/ticket_list.html', {'tickets': tickets})


def reprint_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    line_items = ticket.line_items.all()
    return render(request, 'sales/reprint_ticket.html', {'ticket': ticket, 'line_items': line_items})


@login_required
def new_sale(request):
    # Carga de productos y clientes para el formulario de la venta
    productos = Product.objects.all()
    clientes = Cliente.objects.all()

    if request.method == 'POST':
        # Obtener datos JSON de la solicitud
        try:
            data = json.loads(request.body)
            cliente_id = data.get('cliente_id')
            productos_data = data.get('productos', [])

            # Cálculo del total de la venta
            total_compra = Decimal('0.00')
            for producto_data in productos_data:
                producto_id = producto_data.get('id')
                cantidad = producto_data.get('cantidad')
                precio_unitario = parse_decimal(str(producto_data.get('precio_unitario')))  # Usar parse_decimal
                producto = Product.objects.get(id=producto_id)

                if producto.se_vende_fraccionado:
                    # Si el producto se vende por fracción, el precio se calcula por gramos (o kilos)
                    precio_unitario_por_gramo = precio_unitario / 1000
                    total_producto = precio_unitario_por_gramo * cantidad
                else:
                    total_producto = precio_unitario * cantidad

                total_compra += total_producto

            # Crear la venta
            venta = Venta(cliente_id=cliente_id, total=total_compra, fecha_venta=timezone.now())
            venta.save()

            # Agregar los detalles de la venta
            for producto_data in productos_data:
                producto_id = producto_data.get('id')
                cantidad = producto_data.get('cantidad')
                producto = Product.objects.get(id=producto_id)
                precio_unitario = parse_decimal(str(producto_data.get('precio_unitario')))  # Usar parse_decimal

                if producto.se_vende_fraccionado:
                    # Si el producto se vende por fracción, ajustamos la cantidad
                    total_producto = precio_unitario * (cantidad / 1000)
                else:
                    total_producto = precio_unitario * cantidad

                detalle_venta = DetalleVenta(
                    venta=venta,
                    producto_id=producto_id,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    total=total_producto
                )
                detalle_venta.save()

            return JsonResponse({'success': True, 'ticket_id': venta.id})

        except Exception as e:
            print(f"Error en la venta: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    # Renderizar el formulario de venta si no es una petición POST
    return render(request, 'sales/new_sale.html', {'productos': productos, 'clientes': clientes})



def buscar_venta(request):
    # lógica para buscar venta
    return render(request, 'sales/buscar_venta.html')

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

# Nueva vista para ProductDetailView
def product_detail(request, product_id):
    return get_product(request, product_id)


@login_required
def ticket_detail(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    line_items = LineItem.objects.filter(ticket=ticket)
    print("Line items in ticket detail:", line_items)


    return render(request, 'sales/ticket_detail.html', {
        'ticket': ticket,
        'line_items': line_items
    })

@csrf_exempt
@login_required
def realizar_venta(request):
    if request.method == 'POST':
        try:
            # Imprimir el cuerpo de la solicitud para depuración
            print("JSON recibido:", request.body.decode('utf-8'))
            
            data = json.loads(request.body)
            cliente_id = data.get('cliente_id')
            productos_data = data.get('productos', [])
            total_compra = data.get('total', 0)

            if not cliente_id or not productos_data or total_compra is None:
                return JsonResponse({"success": False, "message": "Faltan datos de cliente, productos o total."}, status=400)

            cliente = get_object_or_404(Cliente, id=cliente_id)
            venta = Venta.objects.create(cliente=cliente, fecha_venta=timezone.now(), total=total_compra)

            # Obtener el usuario actual (cajero)
            cajero = request.user

            # Crear el ticket con el cajero asignado
            ticket = Ticket.objects.create(
                venta=venta,
                date=timezone.now(),
                total=total_compra,
                cashier_id=cajero.id  # Asignar el cajero
            )

            for item in productos_data:
                product_id = item.get('id')
                cantidad = int(item.get('cantidad'))  # Asegurarse de que sea un número entero
                total_producto = Decimal(item.get('total'))  # Convertir total a Decimal
                precio_unitario = Decimal(item.get('precio_unitario'))  # Convertir a Decimal

                product = get_object_or_404(Product, id=product_id)

                # Crear el detalle de la venta
                detalle_venta = DetalleVenta.objects.create(
                    venta=venta,
                    producto=product,
                    cantidad=cantidad,
                    total=total_producto,
                    precio_unitario=precio_unitario
                )

                # Crear el LineItem
                LineItem.objects.create(  
                    ticket=ticket,
                    product=product,      
                    quantity=cantidad,    
                    subtotal=total_producto  # Asegurarse de que 'subtotal' sea Decimal
                )

            # Devolver un JSON con el éxito y el ID del ticket
            return JsonResponse({
                "success": True,
                "message": "Venta procesada correctamente",
                "ticket_id": ticket.id
            })


            # return redirect('sales:ticket_detail', ticket_id=ticket.id)  # Redirigir usando el ID del ticket

        except Exception as e:
            print(f"Error al procesar la venta: {e}")
            return JsonResponse({"success": False, "message": "Hubo un error al procesar la venta. Inténtalo nuevamente."}, status=500)


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