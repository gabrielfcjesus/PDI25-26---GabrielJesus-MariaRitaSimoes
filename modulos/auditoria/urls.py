from django.urls import path
from . import views

app_name = 'auditoria'

urlpatterns = [
    path('', views.logs_lista, name='lista'),
    path('<int:pk>/', views.log_detalhe, name='detalhe'),
]
