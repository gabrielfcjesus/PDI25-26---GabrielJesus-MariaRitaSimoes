from django.urls import path
from . import views
app_name = 'expedicao'
urlpatterns = [
    path('', views.menu, name='menu'),
    path('lista/', views.expedicoes_lista, name='lista'),
    path('criar/', views.criar, name='criar'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
]
