from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from products.models import Product, Categoria
from sales.models import Venta, DetalleVenta
from accounts.models import Cliente
from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


def admin_required(view_func):
    """Decorator to ensure user is admin."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'is_admin') or not request.user.is_admin:
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('dashboard:user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    """Admin dashboard with statistics and management overview."""
    now = timezone.now()
    last_month_start = now - timedelta(days=30)
    previous_month_start = last_month_start - timedelta(days=30)

    products_qs = Product.objects.all()
    total_products = products_qs.count()
    total_stock_amount = products_qs.aggregate(total=Sum('cantidad_stock'))['total'] or Decimal('0')

    total_clients = Cliente.objects.count()
    total_categories = Categoria.objects.count()

    sales_last_month_qs = Venta.objects.filter(fecha_venta__gte=last_month_start)
    total_sales_last_month = sales_last_month_qs.count()
    total_revenue_last_month = sales_last_month_qs.aggregate(total=Sum('total'))['total'] or Decimal('0')
    credit_sales_last_month = sales_last_month_qs.filter(es_fiada=True).count()

    previous_month_revenue = Venta.objects.filter(
        fecha_venta__gte=previous_month_start,
        fecha_venta__lt=last_month_start
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')

    if previous_month_revenue and previous_month_revenue != 0:
        sales_growth_percent = float((total_revenue_last_month - previous_month_revenue) / previous_month_revenue * 100)
    else:
        sales_growth_percent = 100.0 if total_revenue_last_month else 0.0

    # Productos con bajo stock (menos de 10 unidades)
    low_stock_products = Product.objects.filter(cantidad_stock__lt=10).order_by('cantidad_stock')
    low_stock_count = low_stock_products.count()

    # Ventas recientes (últimas 10)
    recent_sales_list = Venta.objects.select_related('cliente').order_by('-fecha_venta')[:10]

    # Tendencia de ventas (últimos 30 días)
    sales_trend_queryset = sales_last_month_qs.annotate(day=TruncDay('fecha_venta')) \
        .values('day').annotate(total=Sum('total')).order_by('day')
    sales_trend = {
        'labels': [entry['day'].strftime('%d/%m') for entry in sales_trend_queryset],
        'data': [float(entry['total'] or 0) for entry in sales_trend_queryset],
    }

    # Productos más vendidos (por ingresos)
    top_products_queryset = DetalleVenta.objects.filter(venta__fecha_venta__gte=last_month_start) \
        .values('producto__nombre').annotate(total_revenue=Sum('total')).order_by('-total_revenue')[:5]
    top_products = {
        'labels': [entry['producto__nombre'] for entry in top_products_queryset],
        'data': [float(entry['total_revenue'] or 0) for entry in top_products_queryset],
    }

    def build_sidebar_links(req):
        links = [
            {'label': 'Dashboard', 'url': reverse('dashboard:admin_dashboard'), 'icon': 'grid'},
            {'label': 'Productos', 'url': reverse('list_products'), 'icon': 'package'},
            {'label': 'Agregar Producto', 'url': reverse('add_products'), 'icon': 'plus'},
            {'label': 'Categorías', 'url': reverse('listar_categorias'), 'icon': 'layers'},
            {'label': 'Clientes', 'url': reverse('listar_clientes'), 'icon': 'users'},
            {'label': 'Nueva Venta', 'url': reverse('sales:new_sale'), 'icon': 'cart'},
            {'label': 'Tickets', 'url': reverse('sales:ticket_list'), 'icon': 'receipt'},
            {'label': 'Reportes', 'url': reverse('reports_dashboard'), 'icon': 'chart'},
            {'label': 'Cuentas Corrientes', 'url': reverse('gestion_cuentas_corrientes'), 'icon': 'wallet'},
        ]
        current_path = req.path
        for link in links:
            link['active'] = current_path.startswith(link['url'])
        return links

    context = {
        'page_title': 'Dashboard Administrador',
        'business_name': 'El Almacén',
        'sidebar_links': build_sidebar_links(request),
        'total_products': total_products,
        'total_stock_amount': total_stock_amount,
        'total_clients': total_clients,
        'credit_sales_last_month': credit_sales_last_month,
        'total_categories': total_categories,
        'total_sales_last_month': total_sales_last_month,
        'total_revenue_last_month': total_revenue_last_month,
        'sales_growth_percent': sales_growth_percent,
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
        'sales_trend': sales_trend,
        'top_products': top_products,
        'recent_sales': recent_sales_list,
    }

    return render(request, 'dashboards/admin_dashboard.html', context)

@login_required
def cashier_dashboard(request):
    """Cashier dashboard - accessible by cashiers and admins."""
    if not (hasattr(request.user, 'is_cashier') and request.user.is_cashier) and \
       not (hasattr(request.user, 'is_admin') and request.user.is_admin):
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard:user_dashboard')
    
    return render(request, 'dashboards/cashier_dashboard.html', {'page_title': 'Dashboard Cajero'})


@login_required
def user_dashboard(request):
    """User dashboard - accessible by all authenticated users."""
    return render(request, 'dashboards/user_dashboard.html', {'page_title': 'Dashboard Usuario'})

