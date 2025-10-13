from django.urls import path
from . import views
from .views import asignar_cuenta_corriente

urlpatterns = [
    path('gestion-cuentas-corrientes/', views.gestion_cuentas_corrientes, name='gestion_cuentas_corrientes'),
    path('crear/', views.crear_cuenta_corriente, name='crear_cuenta_corriente'),
    path('agregar_saldo/<int:cuenta_id>/', views.agregar_saldo, name='agregar_saldo'),
    path('pagar/<int:cuenta_id>/', views.pagar_cuenta, name='pagar_cuenta'),
    path('clientes/<int:cliente_id>/asignar-cuenta/', views.asignar_cuenta_corriente, name='asignar_cuenta_corriente'),
    path('clientes/<int:cliente_id>/eliminar-cuenta/', views.eliminar_cuenta_corriente, name='eliminar_cuenta_corriente'),
    path('editar/<int:pk>/', views.editar_cuenta_corriente, name='editar_cuenta_corriente'),
]
