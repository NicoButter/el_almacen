from django.urls import path, include
from .views import loguin, post_login
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView

app_name = 'accounts'

urlpatterns = [
    path('', loguin, name='login'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('post-login/', post_login, name='post_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
]
