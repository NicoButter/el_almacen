from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
    listar_productos,
    agregar_producto,
    editar_producto,
    eliminar_producto,
    crear_categoria,
    listar_categorias,
    editar_categoria,  
    eliminar_categoria,
    imprimir_qr  
)

urlpatterns = [
    path('', listar_productos, name='listar_productos'),
    path('listar-categorias/', listar_categorias, name='listar_categorias'),
    path('agregar/', agregar_producto, name='add_products'),
    path('crear-categoria/', crear_categoria, name='add_category'),
    path('editar-categoria/<int:categoria_id>/', editar_categoria, name='editar_categoria'),
    path('eliminar-categoria/<int:categoria_id>/', eliminar_categoria, name='eliminar_categoria'),
    path('listar/', listar_productos, name='list_products'),
    path('editar/<int:pk>/', editar_producto, name='edit_products'),
    path('eliminar/<int:pk>/', eliminar_producto, name='delete_product'),
    path('imprimir_qr/', imprimir_qr, name='imprimir_qr'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
