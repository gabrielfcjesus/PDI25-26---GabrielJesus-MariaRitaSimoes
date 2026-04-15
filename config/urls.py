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
    path('', include('modulos.core.urls')),

    # Módulos ERP
    path('rh/', include('modulos.rh.urls')),
    path('planeamento/', include('modulos.planeamento.urls')),
    path('armazem/', include('modulos.armazem.urls')),
    path('producao/', include('modulos.producao.urls')),
    path('qualidade/', include('modulos.qualidade.urls')),
    path('expedicao/', include('modulos.expedicao.urls')),
    path('montagem/', include('modulos.montagem.urls')),
    path('auditoria/', include('modulos.auditoria.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
