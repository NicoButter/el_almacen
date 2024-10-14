from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')

@login_required
def cashier_dashboard(request):
    return render(request, 'dashboards/cashier_dashboard.html')

@login_required
def user_dashboard(request):
    return render(request, 'dashboards/user_dashboard.html')
