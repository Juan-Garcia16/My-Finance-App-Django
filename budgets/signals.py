from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from transactions.models import Gasto
from budgets.models import Presupuesto


def _mes_key_from_date(fecha):
    return f"{fecha.year:04d}-{fecha.month:02d}"


@receiver(pre_save, sender=Gasto)
def gasto_pre_save(sender, instance, **kwargs):
    # Si existe en DB, guardar estado previo para poder revertir en post_save
    if instance.pk:
        try:
            old = Gasto.objects.get(pk=instance.pk)
            instance._prev_monto = old.monto
            instance._prev_categoria_id = old.categoria_id
            instance._prev_fecha = old.fecha
        except Gasto.DoesNotExist:
            instance._prev_monto = 0
            instance._prev_categoria_id = None
            instance._prev_fecha = None
    else:
        instance._prev_monto = 0
        instance._prev_categoria_id = None
        instance._prev_fecha = None


@receiver(post_save, sender=Gasto)
def gasto_post_save(sender, instance, created, **kwargs):
    # Si editamos, primero revertimos el monto anterior en su presupuesto (si aplica)
    try:
        # Revertir monto anterior si fue editado
        prev_monto = getattr(instance, '_prev_monto', 0) or 0
        prev_categoria_id = getattr(instance, '_prev_categoria_id', None)
        prev_fecha = getattr(instance, '_prev_fecha', None)

        if prev_monto and prev_categoria_id and prev_fecha:
            mes_key_prev = _mes_key_from_date(prev_fecha)
            try:
                presupuesto_prev = Presupuesto.objects.get(usuario=instance.usuario, categoria_id=prev_categoria_id, mes=mes_key_prev)
                presupuesto_prev.actualizar_gasto(-prev_monto)
            except Presupuesto.DoesNotExist:
                pass

        # Ahora aplicar el monto actual al presupuesto correspondiente
        mes_key = _mes_key_from_date(instance.fecha)
        try:
            presupuesto = Presupuesto.objects.get(usuario=instance.usuario, categoria=instance.categoria, mes=mes_key)
            # si es creación, sumar monto; si edición, sumar la diferencia
            delta = instance.monto
            if prev_monto:
                delta = instance.monto  # ya revertimos el anterior
            presupuesto.actualizar_gasto(delta)
            # Si supera límite, podríamos crear alertas (mensajes) en la vista; aquí solo actualizamos
        except Presupuesto.DoesNotExist:
            pass
    except Exception:
        # defensivo: no romper la transacción si algo falla en el módulo de presupuestos
        pass


@receiver(post_delete, sender=Gasto)
def gasto_post_delete(sender, instance, **kwargs):
    try:
        mes_key = _mes_key_from_date(instance.fecha)
        try:
            presupuesto = Presupuesto.objects.get(usuario=instance.usuario, categoria=instance.categoria, mes=mes_key)
            presupuesto.actualizar_gasto(-instance.monto)
        except Presupuesto.DoesNotExist:
            pass
    except Exception:
        pass
