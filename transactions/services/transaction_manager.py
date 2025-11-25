from transactions.models import Ingreso, Gasto
from budgets.models import Presupuesto
from categories.models import Category

class TransactionManager:
    def __init__(self, usuario):
        self.usuario = usuario

    def registrar_transaccion(self, tipo, categoria, monto, fecha, descripcion=""):
        categoria_obj = Category.objects.get(id=categoria, usuario=self.usuario)

        if tipo == "ingreso":
            transaccion = Ingreso(
                usuario=self.usuario,
                categoria=categoria_obj,
                monto=monto,
                fecha=fecha,
                descripcion=descripcion,
            )
        else:
            transaccion = Gasto(
                usuario=self.usuario,
                categoria=categoria_obj,
                monto=monto,
                fecha=fecha,
                descripcion=descripcion,
            )

        # polimorfismo: cada tipo implementa su lógica
        transaccion.registrar()

        # actualización automática de presupuestos
        self._actualizar_presupuestos(categoria_obj, monto, tipo)

        return transaccion

    def _actualizar_presupuestos(self, categoria, monto, tipo):
        # solo gastos afectan presupuesto
        if tipo == "gasto":
            try:
                presupuesto = Presupuesto.objects.get(
                    usuario=self.usuario, categoria=categoria
                )
                presupuesto.actualizar_gasto(monto)
            except Presupuesto.DoesNotExist:
                pass
