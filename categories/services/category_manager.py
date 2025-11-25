from categories.models import Category

class CategoryManager:
    def __init__(self, usuario):
        self.usuario = usuario

    # Crear una nueva categoría
    def crear_categoria(self, nombre, tipo, color="#22C55E"):
        # evitar duplicados por usuario
        if Category.objects.filter(usuario=self.usuario, nombre=nombre, tipo=tipo).exists():
            raise ValueError("La categoría ya existe.")

        return Category.objects.create(
            usuario=self.usuario,
            nombre=nombre,
            tipo=tipo,
            color=color
        )

    # Obtener todas las categorías del usuario
    def obtener_categorias(self):
        return Category.objects.filter(usuario=self.usuario)

    # Obtener solo categorías de tipo ingreso o gasto
    def categorias_por_tipo(self, tipo):
        return Category.objects.filter(usuario=self.usuario, tipo=tipo)

    # Editar categoría
    def editar_categoria(self, categoria_id, nuevo_nombre=None, nuevo_color=None):
        categoria = Category.objects.get(id=categoria_id, usuario=self.usuario)

        if nuevo_nombre:
            categoria.nombre = nuevo_nombre
        if nuevo_color:
            categoria.color = nuevo_color

        categoria.save()
        return categoria

    # Eliminar categoría (solo si no tiene dependencias)
    def eliminar_categoria(self, categoria_id):
        categoria = Category.objects.get(id=categoria_id, usuario=self.usuario)

        # Regla de negocio:
        # No permitir eliminar categoría que tenga transacciones o presupuestos
        if categoria.transaccion_set.exists() or categoria.presupuesto_set.exists():
            raise ValueError("No se puede eliminar esta categoría porque tiene registros asociados.")

        categoria.delete()
        return True
