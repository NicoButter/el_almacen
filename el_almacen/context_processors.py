"""
Context Processors Globales
Estas funciones se ejecutan automáticamente en cada request
y añaden variables al contexto de todos los templates.
"""

from django.urls import reverse


def sidebar_context(request):
    """
    Proporciona el contexto del sidebar para todas las vistas.
    
    Este context processor añade automáticamente:
    - business_name: Nombre del negocio
    - sidebar_links: Lista de links de navegación con estado activo
    
    Esto elimina la necesidad de que cada vista construya
    manualmente los links del sidebar.
    """
    
    # Información del negocio (podría venir de la BD o settings)
    business_name = 'El Almacén'
    
    # Construir los links del sidebar
    sidebar_links = [
        {
            'label': 'Dashboard',
            'url': reverse('dashboard:admin_dashboard'),
            'icon': 'grid'
        },
        {
            'label': 'Productos',
            'url': reverse('list_products'),
            'icon': 'package'
        },
        {
            'label': 'Categorías',
            'url': reverse('listar_categorias'),
            'icon': 'layers'
        },
        {
            'label': 'Clientes',
            'url': reverse('listar_clientes'),
            'icon': 'users'
        },
        {
            'label': 'Ventas',
            'url': reverse('sales:sales_dashboard'),
            'icon': 'cart'
        },
        {
            'label': 'Tickets',
            'url': reverse('sales:ticket_list'),
            'icon': 'receipt'
        },
        {
            'label': 'Reportes',
            'url': reverse('reports_dashboard'),
            'icon': 'chart'
        },
        {
            'label': 'Cuentas Corrientes',
            'url': reverse('gestion_cuentas_corrientes'),
            'icon': 'wallet'
        },
    ]
    
    # Marcar el link activo según la URL actual
    current_path = request.path
    for link in sidebar_links:
        link['active'] = current_path.startswith(link['url'])
    
    return {
        'business_name': business_name,
        'sidebar_links': sidebar_links,
    }
