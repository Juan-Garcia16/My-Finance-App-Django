from django.db import models
from users.models import Profile
from categories.models import Category

# Create your models here.

class Presupuesto(models.Model):
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Category, on_delete=models.CASCADE)
    mes = models.CharField(max_length=20)
    limite = models.DecimalField(max_digits=12, decimal_places=2)
    gasto_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def actualizar_gasto(self, monto):
        self.gasto_actual += monto
        self.save()

    def verificar_limite(self):
        '''Verifica si el gasto actual ha alcanzado o superado el límite del presupuesto (True/False)'''
        return self.gasto_actual >= self.limite 

    def __str__(self):
        return f"{self.categoria.nombre} - {self.mes}"
