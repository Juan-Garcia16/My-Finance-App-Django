from django.db import models
from users.models import Profile
from decimal import Decimal

# Create your models here.

class MetaAhorro(models.Model):
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    monto_objetivo = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_limite = models.DateField()
    progreso = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def actualizar_progreso(self, monto):
        # Asegurarse que usamos Decimal para sumar y no superar el objetivo
        try:
            monto_dec = Decimal(monto)
        except Exception:
            monto_dec = Decimal(str(monto))

        nuevo = (self.progreso or Decimal('0')) + monto_dec
        if self.monto_objetivo and nuevo >= self.monto_objetivo:
            self.progreso = self.monto_objetivo
        else:
            self.progreso = nuevo
        self.save()

    def porcentaje_progreso(self):
        # Evitar división por cero y usar Decimal para precisión
        if not self.monto_objetivo or self.monto_objetivo == 0:
            return 0
        try:
            return (Decimal(self.progreso) / Decimal(self.monto_objetivo)) * 100
        except Exception:
            return 0

    def __str__(self):
        return f"{self.nombre} - {self.porcentaje_progreso():.1f}%"
