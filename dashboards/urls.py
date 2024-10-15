from django.urls import path
from .views import admin_dashboard, cashier_dashboard, user_dashboard

urlpatterns = [
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('cashier_dashboard/', cashier_dashboard, name='cashier_dashboard'),
    path('user_dashboard/', user_dashboard, name='user_dashboard'),
]
