from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.reportes, name='reportes'),
    path('exportar/<str:tipo>/', views.exportar, name='exportar'),
]
