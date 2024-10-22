from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Ticket,  LineItem
from .forms import NewSaleForm  
from django.contrib.auth.decorators import login_required
from products.models import Product


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

            return redirect('sales:detalle_venta', pk=ticket.id)  # Redirigir al detalle de la venta
    else:
        form = NewSaleForm()

    return render(request, 'sales/new_sale.html', {
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
            "precio": str(product.precio),  # Asegúrate de que el precio se envíe como string
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)

# Nueva vista para ProductDetailView
def product_detail(request, product_id):
    return get_product(request, product_id)