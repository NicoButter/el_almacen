from django.urls import path, include
from . import views

urlpatterns = [
    path('agregar/', views.agregar_cliente, name='agregar_cliente'),  
    path('listar/', views.listar_clientes, name='listar_clientes'),  
    path('editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),  
    path('eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
    # path('dashboard/', include('dashboards.urls')),
]
