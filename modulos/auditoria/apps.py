from django.apps import AppConfig


class AuditoriaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modulos.auditoria'
    verbose_name = 'Auditoria'

    def ready(self):
        import modulos.auditoria.signals  # noqa: F401
