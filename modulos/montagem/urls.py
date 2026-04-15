from django.urls import path
from . import views
app_name = 'montagem'
urlpatterns = [
    path('', views.menu, name='menu'),
    path('tarefas/', views.tarefas_lista, name='tarefas'),
    path('tarefas/criar/', views.criar, name='criar'),
    path('guias/', views.guias_lista, name='guias'),
    path('guias/<int:pk>/', views.guia_detalhe, name='guia-detalhe'),
]
