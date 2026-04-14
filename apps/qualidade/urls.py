from django.urls import path
from . import views
app_name = 'qualidade'
urlpatterns = [
    path('', views.menu, name='menu'),
    path('inspecoes/', views.inspecoes_lista, name='inspecoes'),
    path('verificar/', views.verificar, name='verificar'),
    path('ops/<int:pk>/', views.op_detalhe, name='op-detalhe'),
]
