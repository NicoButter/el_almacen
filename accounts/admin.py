from django.contrib import admin
from .models import CustomUser, Cliente, Telefono, Direccion, Email

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_admin', 'is_cashier')
    list_filter = ('is_admin', 'is_cashier', 'is_staff', 'is_active')

admin.site.register(CustomUser, CustomUserAdmin)


class TelefonoInline(admin.TabularInline):
    model = Telefono
    extra = 1

class DireccionInline(admin.TabularInline):
    model = Direccion
    extra = 1

class EmailInline(admin.TabularInline):
    model = Email
    extra = 1

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'user')
    inlines = [TelefonoInline, DireccionInline, EmailInline]

admin.site.register(Cliente, ClienteAdmin)
