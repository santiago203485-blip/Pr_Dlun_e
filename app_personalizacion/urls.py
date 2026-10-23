from django.urls import path

from . import views

app_name = 'personalizacion'

urlpatterns = [
    path('', views.mis_disenos, name='mis_disenos'),
    path('nuevo/', views.nuevo_diseno, name='nuevo'),
    path('<int:pk>/responder/', views.responder_cotizacion, name='responder'),
    path('gestion/', views.gestion_disenos, name='gestion'),
    path('gestion/<int:pk>/', views.gestion_detalle, name='gestion_detalle'),
]
