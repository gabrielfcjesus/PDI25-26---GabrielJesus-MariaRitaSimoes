from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'username_cache', 'acao', 'modulo', 'descricao_curta', 'ip', 'status_code')
    list_filter = ('acao', 'modulo')
    search_fields = ('username_cache', 'descricao', 'endpoint', 'ip')
    readonly_fields = [f.name for f in AuditLog._meta.get_fields() if hasattr(f, 'name')]
    date_hierarchy = 'timestamp'

    def descricao_curta(self, obj):
        return obj.descricao[:80] if obj.descricao else '—'
    descricao_curta.short_description = 'Descrição'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
