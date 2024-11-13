from django.urls import path
from . import views

app_name = 'sales' 

urlpatterns = [
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/reprint/<int:ticket_id>/', views.reprint_ticket, name='reprint_ticket'),
    path('nueva-venta/', views.new_sale, name='new_sale'),
    path('buscar/', views.buscar_venta, name='buscar_venta'),
    path('api/productos/<int:product_id>/', views.product_detail, name='product_detail'),
    path('api/realizar-venta/', views.realizar_venta, name='realizar_venta'),
    path('ticket/pdf/<int:ticket_id>/', views.generar_pdf, name='generar_pdf'),
    path('ticket/email/<int:ticket_id>/', views.enviar_ticket_email, name='enviar_ticket_email'),
    path('ticket/whatsapp/<int:ticket_id>/', views.generar_pdf_whatsapp, name='generar_pdf_whatsapp'),
]
