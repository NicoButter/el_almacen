from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register, user_login
from dashboards.views import admin_dashboard, cashier_dashboard, user_dashboard


urlpatterns = [
    path('login/', user_login, name='login'), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),  
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),  
    path('cashier_dashboard/', cashier_dashboard, name='cashier_dashboard'),  
    path('user_dashboard/', user_dashboard, name='user_dashboard'), 
]
