from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, default='Pendiente')

    def __str__(self):
        return f"{self.user.username} - {self.estado}"