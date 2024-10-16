from django.urls import path
from . import views

app_name = 'sales' 

urlpatterns = [
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/reprint/<int:ticket_id>/', views.reprint_ticket, name='reprint_ticket'),
    path('nueva-venta/', views.new_sale, name='new_sale'),
    path('buscar/', views.buscar_venta, name='buscar_venta'),


]
