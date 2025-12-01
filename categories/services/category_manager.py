from categories.models import Category

class CategoryManager:
    def __init__(self, usuario_profile):
        self.usuario = usuario_profile

    def crear_categoria(self, nombre, tipo, color="#22C55E"):
        '''Crear una nueva categoría para el usuario'''
        # evitar duplicados por usuario
        if Category.objects.filter(usuario=self.usuario, nombre=nombre, tipo=tipo).exists():
            raise ValueError("La categoría ya existe.")

        # categoria creada
        return Category.objects.create(
            usuario=self.usuario,
            nombre=nombre,
            tipo=tipo,
            color=color
        )

    # Obtener todas las categorías del usuario
    def obtener_categorias(self):
        '''Devuelve un QuerySet con todas las categorías del usuario'''
        return Category.objects.filter(usuario=self.usuario)

    def categorias_por_tipo(self, tipo):
        '''Devuelve categorías filtradas por tipo (ingreso/gasto) en QuerySer'''
        return Category.objects.filter(usuario=self.usuario, tipo=tipo)


    def editar_categoria(self, categoria_id, nuevo_nombre=None, nuevo_color=None, nuevo_tipo=None):
        '''Reemplaza los valores en el objeto Category y lo guarda en la DB actualizado'''
        categoria = Category.objects.get(id=categoria_id, usuario=self.usuario)

        if nuevo_nombre:
            categoria.nombre = nuevo_nombre
        if nuevo_color:
            categoria.color = nuevo_color
        if nuevo_tipo:
            categoria.tipo = nuevo_tipo

        categoria.save()
        return categoria

    def eliminar_categoria(self, categoria_id):
        '''Eliminar categoría de la DB (solo si no tiene dependencias)'''
        categoria = Category.objects.get(id=categoria_id, usuario=self.usuario)

        # No permitir eliminar categoría que tenga transacciones (Ingresos/Gastos) o presupuestos
        has_ingresos = hasattr(categoria, 'ingreso_set') and categoria.ingreso_set.exists()
        has_gastos = hasattr(categoria, 'gasto_set') and categoria.gasto_set.exists()
        has_presupuestos = hasattr(categoria, 'presupuesto_set') and categoria.presupuesto_set.exists()
        if has_ingresos or has_gastos or has_presupuestos:
            raise ValueError("No se puede eliminar esta categoría porque tiene registros asociados.")

        categoria.delete()
        return True
