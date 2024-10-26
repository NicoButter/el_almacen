from django.urls import path, include
from .views import admin_dashboard, cashier_dashboard, user_dashboard
from django.conf.urls.static import static



urlpatterns = [
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    # path('editar-producto/<int:pk>/', editar_producto, name='editar_producto'),
    # path('eliminar-producto/<int:pk>/', eliminar_producto, name='eliminar_producto'),
    path('cashier_dashboard/', cashier_dashboard, name='cashier_dashboard'),
    path('user_dashboard/', user_dashboard, name='user_dashboard'),
    path('clients/', include('clients.urls')),
    path('products/', include('products.urls'))
]
