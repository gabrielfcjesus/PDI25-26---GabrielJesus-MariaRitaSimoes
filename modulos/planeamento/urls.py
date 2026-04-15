from django.urls import path
from . import views
app_name = 'planeamento'
urlpatterns = [
    path('', views.ops_lista, name='ops'),
    path('ops/criar/', views.op_criar, name='op-criar'),
    path('ops/<int:pk>/', views.op_detalhe, name='op-detalhe'),
    path('ops/<int:pk>/editar/', views.op_editar, name='op-editar'),
    path('ops/<int:pk>/eliminar/', views.op_eliminar, name='op-eliminar'),
    path('clientes/', views.clientes_lista, name='clientes'),
    path('clientes/criar-ajax/', views.cliente_criar_ajax, name='cliente-criar-ajax'),
    path('clientes/<int:pk>/', views.cliente_detalhe, name='cliente-detalhe'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente-editar'),
    path('clientes/<int:pk>/eliminar/', views.cliente_eliminar, name='cliente-eliminar'),
]
