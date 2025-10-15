from io import BytesIO

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404

from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from products.models import Product, Categoria
from sales.models import Venta
from cuentas_corrientes.models import CuentaCorriente
from accounts.models import Cliente

from datetime import date, datetime, timedelta

#-----------------------------------------------------------------------------------------------------------------------------------

def reports_dashboard(request):
    return render(request, 'reports/reports_dashboard.html', {'page_title': 'Reportes'})

#-----------------------------------------------------------------------------------------------------------------------------------

def inventory_report_pdf(request):
    # Obtener parámetros de filtrado desde la URL o formulario
    categoria_id = request.GET.get('categoria')
    min_stock = request.GET.get('min_stock')

    # Filtrar productos según los criterios
    productos = Product.objects.all()

    # Filtrar por categoría si se seleccionó
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    # Filtrar por stock mínimo si se especificó
    if min_stock:
        productos = productos.filter(cantidad_stock__gte=min_stock)

    # Configurar el PDF
    buffer = BytesIO()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.pdf"'

    p = canvas.Canvas(buffer, pagesize=landscape(A4))

    # Agregar encabezado y pie
    almacen_nombre = "Almacén Central"
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def agregar_encabezado_y_pie():
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 550, f"{almacen_nombre} - Inventario")
        p.setFont("Helvetica", 10)
        p.drawString(50, 530, f"Fecha y Hora: {fecha_hora}")
        p.line(50, 520, 790, 520)  # Línea separadora
        p.setFont("Helvetica-Oblique", 9)
        p.drawString(50, 30, "El Almacen Sistemas")
        p.drawRightString(780, 30, "Página 1")  # Página 1 como ejemplo

    # Crear los datos del PDF
    encabezados = [
        "Nombre del Producto", "Descripción", "Costo", "% Ganancia",
        "Precio Venta", "Stock", "Fraccionado", "Categoría"
    ]

    datos = [
        [
            producto.nombre,
            (producto.descripcion[:30] + "...") if len(producto.descripcion) > 30 else producto.descripcion,
            f"${producto.costo:.2f}",
            f"{producto.porcentaje_ganancia:.2f}%",
            f"${producto.precio_venta:.2f}",
            str(producto.cantidad_stock),
            "Sí" if producto.se_vende_fraccionado else "No",
            producto.categoria.nombre if producto.categoria else "Sin categoría"
        ]
        for producto in productos
    ]

    # Estilos de la tabla
    tabla = Table([encabezados] + datos, colWidths=[120, 150, 70, 70, 70, 50, 70, 100])
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ])
    tabla.setStyle(estilo_tabla)

    # Dibujar la tabla en el PDF
    filas_por_pagina = 20
    total_filas = len(datos)
    inicio = 0

    while inicio < total_filas:
        agregar_encabezado_y_pie()

        # Crear y dibujar la tabla
        tabla_fragmento = Table(
            [encabezados] + datos[inicio:inicio + filas_por_pagina],
            colWidths=[120, 150, 70, 70, 70, 50, 70, 100]
        )
        tabla_fragmento.setStyle(estilo_tabla)
        tabla_fragmento.wrapOn(p, 50, 50)
        tabla_fragmento.drawOn(p, 50, 100)

        # Avanzar a la siguiente página si es necesario
        inicio += filas_por_pagina
        if inicio < total_filas:
            p.showPage()

    # Finalizar y guardar el PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    response.write(buffer.getvalue())
    return response

#-----------------------------------------------------------------------------------------------------------------------------------

def reporte_ventas_pdf(request):
    # Fechas para los filtros
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)
    inicio_anio = hoy.replace(month=1, day=1)

    # Ventas del día
    ventas_dia = Venta.objects.filter(fecha_venta__date=hoy)
    total_ventas_dia = ventas_dia.aggregate(Sum('total'))['total__sum'] or 0
    total_fiado_dia = ventas_dia.filter(es_fiada=True).aggregate(Sum('total'))['total__sum'] or 0

    # Ventas de la semana
    ventas_semana = Venta.objects.filter(fecha_venta__date__gte=inicio_semana)
    total_ventas_semana = ventas_semana.aggregate(Sum('total'))['total__sum'] or 0
    total_fiado_semana = ventas_semana.filter(es_fiada=True).aggregate(Sum('total'))['total__sum'] or 0

    # Ventas del mes
    ventas_mes = Venta.objects.filter(fecha_venta__date__gte=inicio_mes)
    total_ventas_mes = ventas_mes.aggregate(Sum('total'))['total__sum'] or 0
    total_fiado_mes = ventas_mes.filter(es_fiada=True).aggregate(Sum('total'))['total__sum'] or 0

    # Ventas del año
    ventas_anio = Venta.objects.filter(fecha_venta__date__gte=inicio_anio)
    total_ventas_anio = ventas_anio.aggregate(Sum('total'))['total__sum'] or 0
    total_fiado_anio = ventas_anio.filter(es_fiada=True).aggregate(Sum('total'))['total__sum'] or 0

    # Ventas de un período personalizado
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    ventas_periodo = None
    total_ventas_periodo = 0
    total_fiado_periodo = 0

    if fecha_inicio and fecha_fin:
        ventas_periodo = Venta.objects.filter(
            fecha_venta__date__range=[fecha_inicio, fecha_fin]
        )
        total_ventas_periodo = ventas_periodo.aggregate(Sum('total'))['total__sum'] or 0
        total_fiado_periodo = ventas_periodo.filter(es_fiada=True).aggregate(Sum('total'))['total__sum'] or 0

    # Crear el PDF
    buffer = BytesIO()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'

    p = canvas.Canvas(buffer, pagesize=landscape(letter))  # Usar tamaño apaisado

    # Título y Fecha
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 550, "Reporte de Ventas")
    p.setFont("Helvetica", 10)
    p.drawString(50, 530, f"Fecha de Generación: {hoy}")

    # Separador
    p.line(50, 520, 790, 520)

    # Encabezado de la tabla
    encabezados = ["Periodo", "Total Vendido", "Total Fiado"]
    datos_reporte = [
        ("Hoy", total_ventas_dia, total_fiado_dia),
        ("Semana", total_ventas_semana, total_fiado_semana),
        ("Mes", total_ventas_mes, total_fiado_mes),
        ("Año", total_ventas_anio, total_fiado_anio),
    ]

    if ventas_periodo:
        datos_reporte.append(("Período Personalizado", total_ventas_periodo, total_fiado_periodo))

    # Crear los datos de la tabla
    datos = [
        [
            periodo, 
            f"${total_venta:.2f}",
            f"${total_fiado:.2f}"
        ] for periodo, total_venta, total_fiado in datos_reporte
    ]

    # Estilos de la tabla
    tabla = Table([encabezados] + datos, colWidths=[150, 150, 150])
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ])
    tabla.setStyle(estilo_tabla)

    # Dibujar la tabla en el PDF
    tabla.wrapOn(p, 50, 50)
    tabla.drawOn(p, 50, 400)

    # Pie de página
    p.setFont("Helvetica", 8)
    p.drawString(50, 30, "Reporte generado por Sistema de Ventas")
    p.drawRightString(780, 30, f"Página 1")

    # Guardar y devolver el archivo PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    response.write(buffer.getvalue())
    return response

#-----------------------------------------------------------------------------------------------------------------------------------

def inventory_report(request):
    categoria_id = request.GET.get('categoria')
    min_stock = request.GET.get('min_stock', 0)

    # Filtrado de productos según los parámetros
    productos = Product.objects.all()

    # Si se seleccionó una categoría específica, filtramos por ella
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    # Filtramos por stock mínimo si se ha indicado
    if min_stock:
        productos = productos.filter(cantidad_stock__gte=min_stock)

    categorias = Categoria.objects.all()

    return render(request, 'reports/reporte_inventario.html', {
        'productos': productos,
        'categorias': categorias,
        'request': request,  # Para mantener los filtros seleccionados
        'page_title': 'Reporte de Inventario'
    })

#-----------------------------------------------------------------------------------------------------------------------------------

def reporte_ventas(request):
    # Fechas para los filtros
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)
    inicio_anio = hoy.replace(month=1, day=1)

    # Ventas del día
    ventas_dia = Venta.objects.filter(fecha_venta__date=hoy)
    total_ventas_dia = ventas_dia.aggregate(Sum('total'))['total__sum'] or 0
    total_fiado_dia = ventas_dia.filter(es_fiada=True).aggregate(Sum('total'))['total__sum'] or 0

    # Ventas de la semana
    ventas_semana = Venta.objects.filter(fecha_venta__date__gte=inicio_semana)
    total_ventas_semana = ventas_semana.aggregate(Sum('total'))['total__sum'] or 0
    total_fiado_semana = ventas_semana.filter(es_fiada=True).aggregate(Sum('total'))['total__sum'] or 0

    # Ventas del mes
    ventas_mes = Venta.objects.filter(fecha_venta__date__gte=inicio_mes)
    total_ventas_mes = ventas_mes.aggregate(Sum('total'))['total__sum'] or 0
    total_fiado_mes = ventas_mes.filter(es_fiada=True).aggregate(Sum('total'))['total__sum'] or 0

    # Ventas del año
    ventas_anio = Venta.objects.filter(fecha_venta__date__gte=inicio_anio)
    total_ventas_anio = ventas_anio.aggregate(Sum('total'))['total__sum'] or 0
    total_fiado_anio = ventas_anio.filter(es_fiada=True).aggregate(Sum('total'))['total__sum'] or 0

    # Ventas de un período personalizado
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    ventas_periodo = None
    total_ventas_periodo = 0
    total_fiado_periodo = 0

    if fecha_inicio and fecha_fin:
        ventas_periodo = Venta.objects.filter(
            fecha_venta__date__range=[fecha_inicio, fecha_fin]
        )
        total_ventas_periodo = ventas_periodo.aggregate(Sum('total'))['total__sum'] or 0
        total_fiado_periodo = ventas_periodo.filter(es_fiada=True).aggregate(Sum('total'))['total__sum'] or 0

    # Preparar datos para el gráfico
    grafico_datos = [
        {'etiqueta': 'Día', 'total': float(total_ventas_dia)},
        {'etiqueta': 'Semana', 'total': float(total_ventas_semana)},
        {'etiqueta': 'Mes', 'total': float(total_ventas_mes)},
        {'etiqueta': 'Año', 'total': float(total_ventas_anio)},
    ]

    print(grafico_datos)


    return render(request, 'reports/sales_report.html', {
        'total_ventas_dia': total_ventas_dia,
        'total_fiado_dia': total_fiado_dia,
        'total_ventas_semana': total_ventas_semana,
        'total_fiado_semana': total_fiado_semana,
        'total_ventas_mes': total_ventas_mes,
        'total_fiado_mes': total_fiado_mes,
        'total_ventas_anio': total_ventas_anio,
        'total_fiado_anio': total_fiado_anio,
        'total_ventas_periodo': total_ventas_periodo,
        'total_fiado_periodo': total_fiado_periodo,
        'ventas_periodo': ventas_periodo,
        'grafico_datos': grafico_datos,
        'page_title': 'Reporte de Ventas'
    })

#-----------------------------------------------------------------------------------------------------------------------------------

def reporte_cuentas_corrientes(request):
    # Obtener los filtros si los hay
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        cuentas_corrientes = CuentaCorriente.objects.filter(
            Q(cliente__nombre__icontains=busqueda) |
            Q(cliente__emails__email__icontains=busqueda) |
            Q(cliente__telefonos__numero__icontains=busqueda)
        ).distinct()
    else:
        cuentas_corrientes = CuentaCorriente.objects.all()

    # Resumen
    total_cuentas = cuentas_corrientes.count()
    saldo_total = cuentas_corrientes.aggregate(Sum('saldo'))['saldo__sum'] or 0

    # Pasar al contexto
    context = {
        'cuentas_corrientes': cuentas_corrientes,
        'busqueda': busqueda,
        'total_cuentas': total_cuentas,
        'saldo_total': saldo_total,
        'page_title': 'Reporte de Cuentas Corrientes'
    }

    return render(request, 'reports/reporte_cuentas_corrientes.html', context)

#-----------------------------------------------------------------------------------------------------------------------------------

def cuenta_detalle(request, id):
    cuenta = get_object_or_404(CuentaCorriente, id=id)
    return render(request, 'reports/cuenta_detalle.html', {
        'cuenta': cuenta,
        'page_title': 'Detalle de Cuenta Corriente'
    })

#-----------------------------------------------------------------------------------------------------------------------------------

def buscar_cliente(request):
    busqueda = request.GET.get('busqueda', '')
    clientes = Cliente.objects.all()

    if busqueda:
        # Buscamos por el nombre del cliente, email o teléfono
        clientes = clientes.filter(
            Q(nombre__icontains=busqueda) |  # Busca en el nombre
            Q(user__email__icontains=busqueda) |  # Busca en el email del usuario relacionado
            Q(telefonos__numero__icontains=busqueda)  # Busca en el teléfono relacionado
        ).distinct()  # Distinct para evitar duplicados si un cliente tiene más de un teléfono

    return render(request, 'nombre_del_template.html', {
        'clientes': clientes,
        'busqueda': busqueda,
        'page_title': 'Buscar Clientes'
    })

#-----------------------------------------------------------------------------------------------------------------------------------

