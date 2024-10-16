from django.urls import path
from .views import listar_productos, agregar_producto, editar_producto, eliminar_producto

urlpatterns = [
    path('', listar_productos, name='listar_productos'),
    path('agregar/', agregar_producto, name='add_products'),
    path('listar/', listar_productos, name='list_products'),
    path('editar/<int:pk>/', editar_producto, name='edit_products'),
    path('eliminar/<int:pk>/', eliminar_producto, name='delete_product'),
]
