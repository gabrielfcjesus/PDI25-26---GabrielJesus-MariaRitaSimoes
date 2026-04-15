"""
apps/core/admin.py
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Departamento, Cargo


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'ativo']
    list_filter = ['ativo']


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'departamento', 'ativo']
    list_filter = ['departamento', 'ativo']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('PrimeTool', {'fields': ('departamento', 'cargo', 'telefone', 'foto', 'ativo')}),
    )
    list_display = ['username', 'get_full_name', 'departamento', 'cargo', 'ativo']
    list_filter = ['departamento', 'ativo']
