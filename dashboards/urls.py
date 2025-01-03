from django.urls import path, include
from .views import admin_dashboard, cashier_dashboard, user_dashboard



urlpatterns = [
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('cashier_dashboard/', cashier_dashboard, name='cashier_dashboard'),
    path('user_dashboard/', user_dashboard, name='user_dashboard'),
    path('clients/', include('clients.urls')),
    path('products/', include('products.urls'))
]
