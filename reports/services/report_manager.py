from transactions.models import Ingreso, Gasto
from budgets.models import Presupuesto
from goals.models import MetaAhorro
from categories.models import Category
from django.db.models import Sum

class ReportManager:
    def __init__(self, usuario):
        self.usuario = usuario

    def gastos_por_categoria(self):
        return (
            Gasto.objects.filter(usuario=self.usuario)
            .values("categoria__nombre")
            .annotate(total=Sum("monto"))
        )

    def ingresos_vs_gastos(self):
        ingresos = (
            Ingreso.objects.filter(usuario=self.usuario).aggregate(total=Sum("monto"))["total"] or 0
        )
        gastos = (
            Gasto.objects.filter(usuario=self.usuario).aggregate(total=Sum("monto"))["total"] or 0
        )
        return {"ingresos": ingresos, "gastos": gastos}

    def estado_metas(self):
        return MetaAhorro.objects.filter(usuario=self.usuario)

    def estado_presupuestos(self):
        return Presupuesto.objects.filter(usuario=self.usuario)
