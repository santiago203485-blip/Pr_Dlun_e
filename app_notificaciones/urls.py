from django.urls import path

from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.lista_notificaciones, name='lista'),
    path('whatsapp-masivo/', views.whatsapp_masivo, name='masivo'),
    path('avisame/<int:producto_id>/', views.solicitar_stock, name='solicitar_stock'),
    path('mias/', views.mis_notificaciones, name='mias'),
]
