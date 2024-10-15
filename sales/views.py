from django.shortcuts import render, get_object_or_404
from .models import Ticket

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
