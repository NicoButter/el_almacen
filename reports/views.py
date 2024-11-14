from django.shortcuts import render

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from products.models import Product


def reports_dashboard(request):
    return render(request, 'reports/reports_dashboard.html')

#-----------------------------------------------------------------------------------------------------------------------------------

def report_inventory(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    p.setFont("Helvetica", 12)
    p.drawString(100, 800, "Inventory Report")

    products = Product.objects.all()
    y = 750

    # Report headers
    p.drawString(50, y, "Product Name")
    p.drawString(300, y, "Stock Quantity")
    p.drawString(450, y, "Sale Price")

    y -= 20
    for product in products:
        if y < 50:  # New page if space is running out
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 800

        p.drawString(50, y, product.nombre)
        p.drawString(300, y, str(product.cantidad_stock))
        p.drawString(450, y, f"${product.precio_venta:.2f}")

        y -= 20

    p.showPage()
    p.save()
    return response
