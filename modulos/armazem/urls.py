from django.urls import path
from . import views
app_name = 'armazem'
urlpatterns = [
    path('', views.armazem_menu, name='menu'),
    path('materiais/', views.materiais_lista, name='materiais'),
    path('materiais/novo/', views.material_criar, name='material-criar'),
    path('materiais/pesquisar/', views.materiais_pesquisar, name='materiais-pesquisar'),
    path('materiais/<int:pk>/', views.material_detalhe, name='material-detalhe'),
    # Ordens de compra
    path('pedidos/', views.pedidos_lista, name='pedidos'),
    path('pedidos/criar/', views.pedido_criar, name='pedido-criar'),
    path('pedidos/<int:pk>/', views.pedido_detalhe, name='pedido-detalhe'),
    path('pedidos/<int:pk>/acao/', views.pedido_acao, name='pedido-acao'),
]
