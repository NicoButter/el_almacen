from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('inventory_report_pdf/', views.inventory_report_pdf, name='inventory_report_pdf'),
    path('inventory_report/', views.inventory_report, name='inventory_report'),
    path('reporte-ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('reporte_ventas_pdf/', views.reporte_ventas_pdf, name='reporte_ventas_pdf'),
    path('reporte_cuentas_corrientes/', views.reporte_cuentas_corrientes, name='reporte_cuentas_corrientes'),
    path('cuenta/<int:id>/', views.cuenta_detalle, name='cuenta_detalle'),

]
