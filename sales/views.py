from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Ticket, Venta, DetalleVenta, LineItem
from products.models import Product
from accounts.models import Cliente


def ticket_list(request):
    tickets = Ticket.objects.all().order_by('-date') 
    return render(request, 'sales/ticket_list.html', {'tickets': tickets})

# def ticket_detail(request, ticket_id):
#     ticket = get_object_or_404(Ticket, id=ticket_id)
#     line_items = ticket.line_items.all()
#     return render(request, 'sales/ticket_detail.html', {'ticket': ticket, 'line_items': line_items})

def reprint_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    line_items = ticket.line_items.all()
    return render(request, 'sales/reprint_ticket.html', {'ticket': ticket, 'line_items': line_items})

@login_required
def new_sale(request):
    productos = Product.objects.all()
    clientes = Cliente.objects.all()
    scanned_items = request.session.get('scanned_items', [])

    if request.method == 'POST':
        if 'add_product' in request.POST:
            qr_code_value = request.POST.get('qr_code_value')
            if qr_code_value:
                product = get_object_or_404(Product, id=qr_code_value)
                item = {
                    'product_id': product.id,
                    'name': product.nombre,
                    'price': float(product.precio_venta),
                    'quantity': 1
                }
                
                # Actualizar cantidad o agregar nuevo producto
                for scanned_item in scanned_items:
                    if scanned_item['product_id'] == product.id:
                        scanned_item['quantity'] += 1
                        scanned_item['subtotal'] = scanned_item['quantity'] * scanned_item['price']
                        break
                else:
                    item['subtotal'] = item['price']
                    scanned_items.append(item)

                # Persistir cambios en la sesión
                request.session['scanned_items'] = scanned_items
                request.session.modified = True

        elif 'close_sale' in request.POST:
            cliente_id = request.POST.get('cliente_id')
            cliente = get_object_or_404(Cliente, id=cliente_id)

            total_venta = sum(item['subtotal'] for item in scanned_items)

            ticket = Ticket.objects.create(
                cliente=cliente,
                total=total_venta,
                cashier=request.user,
                fiado=False
            )

            # Crear LineItems
            for item in scanned_items:
                try:
                    product = Product.objects.get(id=item['product_id'])
                    line_item = LineItem.objects.create(
                        ticket=ticket,
                        product=product,  # Asigna el objeto Product directamente
                        quantity=item['quantity'],
                        subtotal=item['subtotal']
                    )
                    print(f"LineItem created: {line_item}")
                except Product.DoesNotExist:
                    print(f"Product with ID {item['product_id']} does not exist")

            request.session['scanned_items'] = []
            request.session.modified = True

            return redirect('sales:ticket_detail', ticket_id=ticket.id)

    return render(request, 'sales/new_sale.html', {
        'clientes': clientes,
        'productos': productos,
        'scanned_items': scanned_items,
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


@login_required
def ticket_detail(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    line_items = LineItem.objects.filter(ticket=ticket)
    print("Line items in ticket detail:", line_items)


    return render(request, 'sales/ticket_detail.html', {
        'ticket': ticket,
        'line_items': line_items
    })
