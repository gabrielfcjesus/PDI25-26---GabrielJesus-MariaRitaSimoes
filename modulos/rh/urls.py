from django.urls import path
from . import views
app_name = 'rh'
urlpatterns = [
    path('', views.trabalhadores_lista, name='trabalhadores'),
    path('<int:pk>/', views.trabalhador_detalhe, name='trabalhador-detalhe'),
]
