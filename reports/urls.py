from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('inventory/', views.report_inventory, name='report_inventory'),
]
