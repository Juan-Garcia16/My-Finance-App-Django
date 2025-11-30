from django.apps import AppConfig


class BudgetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budgets'
    def ready(self):
        # Import signals to connect presupuesto updates with transacciones
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
