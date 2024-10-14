# views.py en la aplicación accounts

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

@login_required
def register(request):
    if not request.user.is_staff:  
        return redirect('login')  

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirigir al inicio de sesión después del registro
    else:
        form = UserCreationForm()
        
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirigir al dashboard correspondiente
                if user.is_admin:
                    return redirect('admin_dashboard')  # Cambia esto según la URL de tu dashboard
                elif user.is_cashier:
                    return redirect('cashier_dashboard')
                else:
                    return redirect('user_dashboard')  # Cambia según sea necesario
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})