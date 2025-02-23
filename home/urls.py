# home/urls.py
from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.pagina_inicial, name='pagina_inicial'),
    path('dashboard/', views.dashboard, name='dashboard')
]
