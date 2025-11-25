from goals.models import MetaAhorro

class GoalManager:
    def __init__(self, usuario_profile):
        self.usuario = usuario_profile

    def crear_meta(self, nombre, monto_objetivo, fecha_limite):
        return MetaAhorro.objects.create(
            usuario=self.usuario,
            nombre=nombre,
            monto_objetivo=monto_objetivo,
            fecha_limite=fecha_limite
        )

    def añadir_progreso(self, meta_id, monto):
        meta = MetaAhorro.objects.get(id=meta_id, usuario=self.usuario)
        meta.actualizar_progreso(monto)
        return meta
