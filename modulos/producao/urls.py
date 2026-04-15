from django.urls import path
from . import views
app_name = 'producao'
urlpatterns = [
    path('', views.menu, name='menu'),
    path('ordens/', views.ordens_lista, name='ordens'),
    path('ordens/<int:pk>/', views.op_detalhe, name='op-detalhe'),
    path('ordens/<int:pk>/pedido-material/', views.pedido_material_criar, name='pedido-material'),
    path('pedidos/<int:pk>/processar/', views.pedido_material_processar, name='pedido-processar'),
    path('atualizar-estado/', views.atualizar_estado, name='atualizar-estado'),
    path('pedir-assistencia/', views.pedir_assistencia, name='pedir-assistencia'),
    path('assistencias/', views.assistencias_lista, name='assistencias'),
    path('assistencias/<int:pk>/responder/', views.assistencia_responder, name='assistencia-responder'),
]
