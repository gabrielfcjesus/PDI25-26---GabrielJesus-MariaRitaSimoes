"""
apps/core/urls.py
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),

    # Gestão de utilizadores
    path('utilizadores/', views.UtilizadoresListView.as_view(), name='utilizadores'),
    path('utilizadores/novo/', views.UtilizadorCreateView.as_view(), name='utilizador-criar'),
    path('utilizadores/<int:pk>/editar/', views.UtilizadorUpdateView.as_view(), name='utilizador-editar'),

    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/ops-sugestoes/', views.ops_sugestoes, name='ops-sugestoes'),
]
