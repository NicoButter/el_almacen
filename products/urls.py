from django.urls import path
from .views import listar_productos, agregar_producto, editar_producto, eliminar_producto, crear_categoria, listar_categorias
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', listar_productos, name='listar_productos'),
    path('listar-categorias/', listar_categorias, name='listar_categorias'),
    path('agregar/', agregar_producto, name='add_products'),
    path('crear-categoria/', crear_categoria, name='add_category'),
    path('listar/', listar_productos, name='list_products'),
    path('editar/<int:pk>/', editar_producto, name='edit_products'),
    path('eliminar/<int:pk>/', eliminar_producto, name='delete_product'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
