from transactions.models import Ingreso, Gasto
from categories.models import Category

class TransactionManager:
    def __init__(self, usuario_profile):
        self.usuario = usuario_profile

    def registrar_transaccion(self, tipo, categoria, monto, fecha, descripcion=""):
        '''Registra una nueva transacción (ingreso o gasto) y actualiza el saldo del usuario'''
        
        # categoria asociada a la transaccion
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
        
        return transaccion



    def listar_transacciones(self):
        '''Devuelve una lista mezclada de ingresos y gastos, cada item tiene 
           atributo 'tipo_transaccion' para identificar'''
        
        # ingresos del usuario especifico
        ingresos = list(Ingreso.objects.filter(usuario=self.usuario))
        for i in ingresos:
            setattr(i, 'tipo_transaccion', 'ingreso')
        gastos = list(Gasto.objects.filter(usuario=self.usuario))
        for g in gastos:
            setattr(g, 'tipo_transaccion', 'gasto')

        # all_tx mezcla ambos tipos de transacciones
        all_tx = ingresos + gastos
        
        # ordenar por fecha descendente
        all_tx.sort(key=lambda x: x.fecha, reverse=True)
        return all_tx

    def eliminar_transaccion(self, tipo, transaccion_id):
        '''Elimina una transacción y revierte su efecto en el saldo del usuario'''
        
        if tipo == 'ingreso':
            trans = Ingreso.objects.get(id=transaccion_id, usuario=self.usuario)
            # restar el ingreso del saldo
            self.usuario.actualizar_saldo(-trans.monto)
            trans.delete()
        else:
            trans = Gasto.objects.get(id=transaccion_id, usuario=self.usuario)
            # revertir gasto en saldo
            self.usuario.actualizar_saldo(trans.monto)
            trans.delete()
        return True

    def editar_transaccion(self, tipo, transaccion_id, nuevo_tipo, nueva_categoria, nuevo_monto, nueva_fecha, nueva_descripcion=""):
        '''Edita una transacción existente y ajusta el saldo del usuario según los cambios'''
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
            antigua.delete()

        # Crear nueva transacción usando el método existente
        return self.registrar_transaccion(nuevo_tipo, nueva_categoria, nuevo_monto, nueva_fecha, nueva_descripcion)
