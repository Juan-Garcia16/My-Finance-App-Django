from django.db import models
from users.models import User

# Create your models here.

class Category(models.Model):
    TIPO_CHOICES = [
        ("ingreso", "Ingreso"),
        ("gasto", "Gasto"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    color = models.CharField(max_length=20, default="#22C55E")  # opcional, útil en UI

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"
