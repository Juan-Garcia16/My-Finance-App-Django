from users.models import User

class UserManagerService:
    def actualizar_moneda(self, usuario, nueva_moneda):
        usuario.moneda_preferida = nueva_moneda
        usuario.save()
        return usuario
