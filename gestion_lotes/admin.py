from django.contrib import admin
from .models import Lote, Mezcla, LoteEnMezcla, Despacho

admin.site.register(Lote)
admin.site.register(Mezcla)
admin.site.register(LoteEnMezcla)
admin.site.register(Despacho)