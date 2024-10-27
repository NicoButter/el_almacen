from django.urls import path, include
from .views import register, user_login
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', user_login, name='login'), 
    path('login/', user_login, name='login'), 
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', register, name='register'),  
]
