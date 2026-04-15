"""
PrimeTool - URLs principais
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Core: autenticação e dashboard
    path('', include('apps.core.urls')),

    # Módulos ERP
    path('rh/', include('apps.rh.urls')),
    path('planeamento/', include('apps.planeamento.urls')),
    path('armazem/', include('apps.armazem.urls')),
    path('producao/', include('apps.producao.urls')),
    path('qualidade/', include('apps.qualidade.urls')),
    path('expedicao/', include('apps.expedicao.urls')),
    path('montagem/', include('apps.montagem.urls')),
    path('auditoria/', include('apps.auditoria.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
