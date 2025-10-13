from django.urls import path, include
from .views import register, user_login
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView



urlpatterns = [
    path('', user_login, name='login'), 
    path('login/', LoginView.as_view(), name='login'),    
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', register, name='register'),  
]
