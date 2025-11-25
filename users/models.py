from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    moneda_preferida = models.CharField(max_length=10, default="COP")
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def actualizar_saldo(self, monto):
        self.saldo_actual += monto
        self.save()

    def __str__(self):
        return self.user.username