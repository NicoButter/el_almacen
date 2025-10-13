from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import CustomUser, Cliente, Telefono, Direccion, Email


class CustomUserAdmin(DjangoUserAdmin):
    model = CustomUser
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_admin',
        'is_cashier',
        'is_client',
        'is_staff',
    )
    list_filter = ('is_admin', 'is_cashier', 'is_client', 'is_staff', 'is_active')

    fieldsets = tuple(list(DjangoUserAdmin.fieldsets) + [
        ('Roles', {'fields': ('is_admin', 'is_cashier', 'is_client')}),
    ])

    add_fieldsets = tuple(list(DjangoUserAdmin.add_fieldsets) + [
        ('Roles', {'fields': ('is_admin', 'is_cashier', 'is_client')}),
    ])


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
