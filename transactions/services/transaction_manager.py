from transactions.models import Ingreso, Gasto
from budgets.models import Presupuesto
from categories.models import Category

class TransactionManager:
    def __init__(self, usuario_profile):
        self.usuario = usuario_profile

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

    def listar_transacciones(self):
        # devuelve lista mezclada de ingresos y gastos, cada item tiene atributo 'tipo' para identificar
        ingresos = list(Ingreso.objects.filter(usuario=self.usuario))
        for i in ingresos:
            setattr(i, 'tipo_transaccion', 'ingreso')
        gastos = list(Gasto.objects.filter(usuario=self.usuario))
        for g in gastos:
            setattr(g, 'tipo_transaccion', 'gasto')

        all_tx = ingresos + gastos
        # ordenar por fecha descendente
        all_tx.sort(key=lambda x: x.fecha, reverse=True)
        return all_tx

    def eliminar_transaccion(self, tipo, transaccion_id):
        # reversa el efecto en el saldo y actualiza presupuesto si aplica
        if tipo == 'ingreso':
            trans = Ingreso.objects.get(id=transaccion_id, usuario=self.usuario)
            # restar el ingreso del saldo
            self.usuario.actualizar_saldo(-trans.monto)
            trans.delete()
        else:
            trans = Gasto.objects.get(id=transaccion_id, usuario=self.usuario)
            # revertir gasto en saldo
            self.usuario.actualizar_saldo(trans.monto)
            # ajustar presupuesto si existe
            try:
                presupuesto = Presupuesto.objects.get(usuario=self.usuario, categoria=trans.categoria)
                presupuesto.actualizar_gasto(-trans.monto)
            except Presupuesto.DoesNotExist:
                pass
            trans.delete()
        return True

    def editar_transaccion(self, tipo, transaccion_id, nuevo_tipo, nueva_categoria, nuevo_monto, nueva_fecha, nueva_descripcion=""):
        # Para simplificar: eliminamos la transacción antigua (revirtiendo efectos) y creamos una nueva
        # Obtener y revertir antigua
        if tipo == 'ingreso':
            antigua = Ingreso.objects.get(id=transaccion_id, usuario=self.usuario)
            # revertir saldo
            self.usuario.actualizar_saldo(-antigua.monto)
            antigua.delete()
        else:
            antigua = Gasto.objects.get(id=transaccion_id, usuario=self.usuario)
            # revertir gasto
            self.usuario.actualizar_saldo(antigua.monto)
            try:
                presupuesto = Presupuesto.objects.get(usuario=self.usuario, categoria=antigua.categoria)
                presupuesto.actualizar_gasto(-antigua.monto)
            except Presupuesto.DoesNotExist:
                pass
            antigua.delete()

        # Crear nueva transacción usando el método existente
        return self.registrar_transaccion(nuevo_tipo, nueva_categoria, nuevo_monto, nueva_fecha, nueva_descripcion)
