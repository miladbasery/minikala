from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'name', 'role', 'balance', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('phone_number', 'name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Credentials', {'fields': ('phone_number', 'password')}),
        ('Personal Info', {'fields': ('name', 'avatar', 'balance', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
