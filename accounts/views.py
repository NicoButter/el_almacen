from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser


def get_dashboard_redirect(user):
    """Helper function to get the correct dashboard redirect for a user."""
    if not user.is_authenticated:
        return redirect('accounts:login')
        
    if isinstance(user, CustomUser):
        if user.is_admin:
            return redirect('dashboard:admin_dashboard')
        if user.is_cashier:
            return redirect('dashboard:cashier_dashboard')
        return redirect('dashboard:user_dashboard')
    return redirect('dashboard:user_dashboard')


def loguin(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Bienvenido {user.username}!')
                    return get_dashboard_redirect(user)
                else:
                    messages.error(request, 'Tu cuenta está desactivada.')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'page_title': 'Iniciar Sesión'
    })


@login_required
def post_login(request):
    """Redirect users to their role-specific dashboard after authentication.

    This view is used as a central target for Django's LoginView and
    for LOGIN_REDIRECT_URL so both class-based and function-based
    logins behave the same.
    """
    user = request.user
    if user.is_authenticated:
        return get_dashboard_redirect(user)
    
    # fallback - should not happen with @login_required
    messages.error(request, 'Debes iniciar sesión para acceder.')
    return redirect('accounts:login')

