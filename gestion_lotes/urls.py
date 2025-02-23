from django.urls import path, include
from . import views

from rest_framework.routers import DefaultRouter
from .views import LoteViewSet

router = DefaultRouter()
router.register(r'lotes', LoteViewSet)  # Crea la API en /api/lotes/

'''urlpatterns = [
    path('api/', include(router.urls)),  # Incluye las rutas de la API
]'''


app_name = 'gestion_lotes'

urlpatterns = [
    path('', views.lista_lotes, name='lista_lotes'),
    path('crear/', views.crear_lote, name='crear_lote'),
    path('editar/<int:lote_id>/', views.editar_lote, name='editar_lote'),
    path('eliminar/<int:lote_id>/',views.eliminar_lote, name='eliminar_lote'),
    path('lotes/<int:pk>/', views.detalle_lote, name='detalle_lote'),
    path('stock_producto', views.stock_producto, name='stock_producto'),
    path('crear_mezcla', views.crear_mezcla, name='crear_mezcla'),
    path('lista_despachos', views.despachos, name="lista_despachos"),
    path('registrar_despacho/<int:pk>', views.registrar_despacho, name="registrar_despacho"),
    path('detalle_mezcla/<int:pk>', views.detalle_mezcla, name="detalle_mezcla"),
    path('nuevo_despacho>', views.nuevo_despacho, name="nuevo_despacho"),
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),
    path('api/', include(router.urls)),
]