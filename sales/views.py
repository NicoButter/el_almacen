from django.shortcuts import render, get_object_or_404, redirect
from .models import Ticket,  LineItem
from .forms import NewSaleForm  # Creamos este formulario más adelante
from django.contrib.auth.decorators import login_required



def ticket_list(request):
    tickets = Ticket.objects.all().order_by('-date')  # Lista de tickets ordenados por fecha
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
    if request.method == 'POST':
        form = NewSaleForm(request.POST)
        if form.is_valid():
            # Guardamos la venta (Ticket) y las líneas (LineItems)
            ticket = form.save(commit=False)
            ticket.cashier = request.user  # Asignar cajero
            ticket.save()

            # Guardar las líneas de productos
            for item in form.cleaned_data['items']:
                LineItem.objects.create(
                    ticket=ticket,
                    product=item['product'],
                    quantity=item['quantity'],
                    subtotal=item['subtotal']
                )

            return redirect('sales:detalle_venta', pk=ticket.id)  # Redirigir al detalle de la venta
    else:
        form = NewSaleForm()

    return render(request, 'sales/new_sale.html', {'form': form})

def buscar_venta(request):
    # Lógica para buscar una venta
    return render(request, 'sales/buscar_venta.html')