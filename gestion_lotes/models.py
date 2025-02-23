from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone


class Lote(models.Model):
    nombre_lote = models.CharField(max_length=25, unique=True)
    fecha_inicio = models.DateField()
    etapa = models.CharField(max_length=25, default='-')
    estado = models.CharField(max_length=15, choices=[('iniciado','Iniciado'), ('finalizado', 'Finalizado')], default='Iniciado')
    producto = models.CharField(max_length=100, choices=[('prod A', 'Prod A'), ('prod B','Prod B'),('prod C','Prod C')], default="No especificado")
    tipo = models.CharField(max_length=20, choices=[('tipo 1', 'Tipo 1'), ('tipo 2', 'Tipo 2'), ('tipo 3', 'Tipo 3')], default=None)
    fecha_fin = models.DateField(null=True, blank=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=1, help_text="Cantidad en kg", null=True, blank=True)
    calidad1 = models.IntegerField(choices=[(i, i) for i in range(1, 11)], help_text="Calidad 1 (1-10)", null=True, blank=True, default=1)
    calidad2 = models.IntegerField(choices=[(i, i) for i in range(1, 11)], help_text="Calidad 2 (1-10)", null=True, blank=True, default=1)
    usado = models.BooleanField(default=False)
    tipo_lote = models.CharField(max_length=20, default='individual')
    STATE_CHOICES = [
        ('Activo', 'Activo'),
        ('Desactivado', 'Desactivado'),
    ]
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='Activo')
    stock = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, default=0)

    def save(self, *args, **kwargs):
        # Si el estado es 'finalizado' y el stock aún no ha sido asignado
        if self.estado == 'finalizado' and self.usado == False:
            self.stock = self.cantidad
        # save() original para guardar el objeto
        super().save(*args, **kwargs)

    #La siguiente linea permite que los objetos se muestren más legible en el administrador de Django
    def __str__(self):
        return f"{self.nombre_lote} - {self.estado}"
    

class Mezcla(models.Model):
    nombre_mezcla = models.CharField(max_length=20, unique=True)
    cantidad_total = models.IntegerField()
    lotes = models.ManyToManyField('Lote', through='LoteEnMezcla')
    destino = models.CharField(max_length=100, blank=True, null=True)
    despachada = models.BooleanField(default=False)
    stock_restante = models.PositiveIntegerField(default=1)
    producto = models.CharField(max_length=100, default="No especificado", null=True)

    '''def save(self, *args, **kwargs):
        # Inicializar el stock restante con la cantidad total si es una nueva mezcla
        if not self.pk:
            self.stock_restante = self.cantidad_total
        super().save(*args, **kwargs)''' #ME GUSTA ESTA IDEA PERO NO ME ESTARIA FUNCIONANDO

    def __str__(self):
        return f"{self.nombre_mezcla}"


class LoteEnMezcla(models.Model):
    mezcla = models.ForeignKey(Mezcla, on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.lote.nombre_lote} en {self.mezcla.nombre_mezcla} ({self.cantidad}kg)"
    

class Despacho(models.Model):
    mezcla = models.ForeignKey(Mezcla, on_delete=models.CASCADE, related_name='despachos')
    cliente = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    fecha_despacho = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Despacho a {self.cliente} - Cantidad: {self.cantidad}"