from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth.views import LogoutView

app_name = 'usuarios'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('cerrar/', LogoutView.as_view(), name='logout'),
    path('aprobar_usuarios/', views.aprobar_usuarios, name='aprobar_usuarios'),
    path('gestion_usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
]
