from django.db import models
from users.models import Profile

# Create your models here.

class MetaAhorro(models.Model):
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    monto_objetivo = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_limite = models.DateField()
    progreso = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def actualizar_progreso(self, monto):
        self.progreso += monto
        self.save()

    def porcentaje_progreso(self):
        return (self.progreso / self.monto_objetivo) * 100

    def __str__(self):
        return f"{self.nombre} - {self.porcentaje_progreso():.1f}%"
