from django.urls import path
from . import views
from .views import asignar_cuenta_corriente

urlpatterns = [
    path('crear/', views.crear_cuenta_corriente, name='crear_cuenta_corriente'),
    path('agregar_saldo/<int:cuenta_id>/', views.agregar_saldo, name='agregar_saldo'),
    path('pagar/<int:cuenta_id>/', views.pagar_cuenta, name='pagar_cuenta'),
    path('asignar-cuenta-corriente/<int:cliente_id>/', asignar_cuenta_corriente, name='asignar_cuenta_corriente')
]
