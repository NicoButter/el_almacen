from django.urls import path, include
from . import views
from cuentas_corrientes.views import asignar_cuenta_corriente



urlpatterns = [
    path('agregar/', views.agregar_cliente, name='agregar_cliente'),  
    path('listar/', views.listar_clientes, name='listar_clientes'),  
    path('editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),  
    path('eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('clientes/<int:cliente_id>/asignar-cuenta/', asignar_cuenta_corriente, name='asignar_cuenta_corriente')
]
