from django.shortcuts import render, get_object_or_404, redirect

from django.views.decorators.csrf import csrf_exempt
import json

from django.http import JsonResponse
from .models import Ticket,  LineItem
from .forms import NewSaleForm  
from django.contrib.auth.decorators import login_required
from products.models import Product
from accounts.models import Cliente
from .models import Venta, ProductoVenta



def ticket_list(request):
    tickets = Ticket.objects.all().order_by('-date') 
    return render(request, 'sales/ticket_list.html', {'tickets': tickets})

def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    line_items = ticket.line_items.all()
    return render(request, 'sales/ticket_detail.html', {'ticket': ticket, 'line_items': line_items})

def reprint_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    line_items = ticket.line_items.all()
    return render(request, 'sales/reprint_ticket.html', {'ticket': ticket, 'line_items': line_items})



@login_required
def new_sale(request):
    productos = Product.objects.all()
    clientes = Cliente.objects.all()
    scanned_items = []  # Inicializar una lista para almacenar productos escaneados

    if request.method == 'POST':
        # Obtenemos el ID escaneado del código QR
        qr_code_value = request.POST.get('qr_code_value')

        if qr_code_value:
            product = get_object_or_404(Product, id=qr_code_value)
            scanned_items.append({'product': product, 'quantity': 1, 'subtotal': product.price})  # Asumiendo que product.price es el precio del producto

        form = NewSaleForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.cashier = request.user  # Asignar cajero
            ticket.save()

            # Guardar las líneas de productos escaneados
            for item in scanned_items:
                LineItem.objects.create(
                    ticket=ticket,
                    product=item['product'],
                    quantity=item['quantity'],
                    subtotal=item['subtotal']
                )

            return redirect('sales:detalle_venta', pk=ticket.id, )  # Redirigir al detalle de la venta
    else:
        form = NewSaleForm()

    return render(request, 'sales/new_sale.html' , {
        'clientes': clientes,
        'form': form,
        'productos': productos,  # Pasar productos a la plantilla
        'scanned_items': scanned_items,  # Pasar productos escaneados a la plantilla
    })


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

@csrf_exempt
def realizar_venta(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cliente_id = data.get('cliente')
        productos = data.get('productos')

        try:
            cliente = Cliente.objects.get(id=cliente_id)
            venta = Venta.objects.create(cliente=cliente, total=0)  # Asigna total 0 temporalmente

            total = 0
            for producto_data in productos:
                producto_id = producto_data.get('id')
                cantidad = producto_data.get('cantidad')
                # Asumir que existe una función para obtener el precio del producto
                precio = obtener_precio_producto(producto_id)
                total_producto = precio * cantidad
                total += total_producto
                ProductoVenta.objects.create(venta=venta, producto_id=producto_id, cantidad=cantidad, total=total_producto)

            venta.total = total
            venta.save()

            return JsonResponse({'success': True})
        except Cliente.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cliente no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})