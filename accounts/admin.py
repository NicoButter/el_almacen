from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_admin', 'is_cashier', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_admin', 'is_cashier', 'is_staff', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_admin', 'is_cashier')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_admin', 'is_cashier')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
