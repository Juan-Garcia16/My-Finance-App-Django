from budgets.models import Presupuesto
from categories.models import Category

class BudgetManager:
    def __init__(self, usuario_profile):
        self.usuario = usuario_profile

    def crear_presupuesto(self, categoria_id, limite, mes):
        '''Crea un nuevo presupuesto para una categoría y mes específicos'''
        categoria = Category.objects.get(id=categoria_id, usuario=self.usuario)
        return Presupuesto.objects.create(
            usuario=self.usuario,
            categoria=categoria,
            limite=limite,
            mes=mes
        )

    def estado_presupuesto(self, categoria_id):
        '''Verifica el estado del presupuesto para una categoría específica (limites del presupuesto)'''
        try:
            presupuesto = Presupuesto.objects.get(
                usuario=self.usuario,
                categoria_id=categoria_id
            )
            return presupuesto.verificar_limite()
        except Presupuesto.DoesNotExist:
            return None
