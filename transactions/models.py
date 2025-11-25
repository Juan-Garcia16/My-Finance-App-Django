from django.db import models
from users.models import Profile
from categories.models import Category
from django.utils import timezone

# Create your models here.

class Transaccion(models.Model):
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Category, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(default=timezone.now)
    descripcion = models.TextField(blank=True)

    class Meta:
        abstract = True  # No crea tabla

    # Encapsulamiento del monto
    def get_monto(self):
        return self.monto

    # polimorfismo
    def registrar(self):
        raise NotImplementedError("Este método debe ser implementado por las subclases.")

    def __str__(self):
        return f"{self.categoria.nombre} - {self.monto}"
    

class Ingreso(Transaccion):

    def registrar(self):
        # saldo aumenta
        self.usuario.actualizar_saldo(self.monto)
        self.save()


class Gasto(Transaccion):

    def registrar(self):
        # saldo disminuye
        self.usuario.actualizar_saldo(-self.monto)
        self.save()
