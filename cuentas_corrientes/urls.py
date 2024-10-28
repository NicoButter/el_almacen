from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_cuenta_corriente, name='crear_cuenta_corriente'),
    path('agregar_saldo/<int:cuenta_id>/', views.agregar_saldo, name='agregar_saldo'),
    path('pagar/<int:cuenta_id>/', views.pagar_cuenta, name='pagar_cuenta')
]
