from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from users.models import Profile
from categories.models import Category
from budgets.models import Presupuesto
from .forms import TransactionForm
from .services.transaction_manager import TransactionManager
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime


def _format_cop(value):
    """Formato numerico para pesos colombianos COP (sin decimales)"""
    if value is None:
        return ''
    try:
        amt = Decimal(value)
    except Exception:
        try:
            amt = Decimal(str(value))
        except Exception:
            return str(value)

    try:
        amt = amt.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    except Exception:
        pass
    try:
        s = "{:,.0f}".format(amt)
    except Exception:
        try:
            s = "{:,.0f}".format(int(amt))
        except Exception:
            return str(value)
    return s.replace(',', '.')


def _evaluate_budget_for_category_month(profile, categoria, fecha):
    """Evalúa el presupuesto asociado a `categoria` en el mes de `fecha`.
    Devuelve un dict: {status, message, pct_display, presupuesto} donde status puede ser
    'over', 'near', 'ok' o None si no aplica.
    """
    try:
        # resolver categoria a objeto si se pasó id
        if categoria is None:
            return {'status': None, 'message': '', 'pct_display': 0, 'presupuesto': None}
        if not hasattr(categoria, 'id'):
            # asumimos id
            categoria_obj = Category.objects.get(id=categoria, usuario=profile)
        else:
            categoria_obj = categoria

        # obtener mes_key
        mes_key = None
        if hasattr(fecha, 'strftime'):
            mes_key = fecha.strftime('%Y-%m')
        else:
            try:
                d = datetime.fromisoformat(str(fecha))
                mes_key = d.strftime('%Y-%m')
            except Exception:
                mes_key = None

        if not mes_key:
            return {'status': None, 'message': '', 'pct_display': 0, 'presupuesto': None}

        presupuesto = Presupuesto.objects.filter(usuario=profile, categoria=categoria_obj, mes=mes_key).first()
        if not presupuesto:
            return {'status': None, 'message': '', 'pct_display': 0, 'presupuesto': None}

        try:
            limite = Decimal(presupuesto.limite)
            gasto_actual = Decimal(presupuesto.gasto_actual)
            pct = (gasto_actual / limite * 100) if limite and limite > 0 else Decimal('0')
        except Exception:
            pct = Decimal('0')

        pct_display = int(min(pct, Decimal('999')))
        if pct >= 100:
            state = 'over'
            message = f"Presupuesto alcanzado/sobrepasado ({pct_display}%)."
        elif pct >= 80:
            state = 'near'
            message = f"Cuidado: presupuesto cerca de llenarse ({pct_display}%)."
        else:
            state = 'ok'
            message = ''

        return {'status': state, 'message': message, 'pct_display': pct_display, 'presupuesto': presupuesto}
    except Exception:
        return {'status': None, 'message': '', 'pct_display': 0, 'presupuesto': None}


@login_required
def transactions_list(request):
    '''Lista todas las transacciones del usuario (ingresos y gastos mezclados)'''
    profile = Profile.objects.get(user=request.user)
    manager = TransactionManager(profile)

    # if request.method == 'POST':
    #     form = TransactionForm(request.POST, usuario=profile)
    #     if form.is_valid():
    #         try:
    #             manager.registrar_transaccion(
    #                 form.cleaned_data['tipo'],
    #                 form.cleaned_data['categoria'].id,
    #                 form.cleaned_data['monto'],
    #                 form.cleaned_data['fecha'],
    #                 form.cleaned_data.get('descripcion', ''),
    #             )
    #             messages.success(request, 'Transacción registrada.', extra_tags='transactions')
    #             return redirect('transactions:list')
    #         except Exception as e:
    #             messages.error(request, str(e), extra_tags='transactions')
    # else:
    #     # formulario en blanco
    form = TransactionForm(usuario=profile)

    transactions = manager.listar_transacciones()

    # Formatear todas las transacciones a COP
    for tx in transactions:
        try:
            tx.monto_display = _format_cop(tx.monto)
        except Exception:
            tx.monto_display = str(tx.monto)
            
            
        # Añadir información de presupuesto cuando aplique (solo para gastos)
        try:
            if getattr(tx, 'tipo_transaccion', '') == 'gasto':
                res = _evaluate_budget_for_category_month(profile, tx.categoria, tx.fecha)
                tx.budget_status = res.get('status')
                tx.budget_message = res.get('message', '')
                tx.budget_pct_display = res.get('pct_display', 0)
        except Exception:
            tx.budget_status = None
            tx.budget_message = ''
            tx.budget_pct_display = 0
    return render(request, 'transactions/transactions.html', {'form': form, 'transactions': transactions})


@login_required
def transactions_create(request):
    '''Crea una nueva transacción (ingreso o gasto)'''
    profile = Profile.objects.get(user=request.user)
    manager = TransactionManager(profile)

    if request.method == 'POST':
        form = TransactionForm(request.POST, usuario=profile)
        if form.is_valid():
            try:
                manager.registrar_transaccion(
                    form.cleaned_data['tipo'],
                    form.cleaned_data['categoria'].id,
                    form.cleaned_data['monto'],
                    form.cleaned_data['fecha'],
                    form.cleaned_data.get('descripcion', ''),
                )
                messages.success(request, 'Transacción registrada.', extra_tags='transactions')
                # después de crear, verificar presupuesto afectado (si es gasto)
                try:
                    if form.cleaned_data['tipo'] == 'gasto':
                        res = _evaluate_budget_for_category_month(profile, form.cleaned_data['categoria'], form.cleaned_data['fecha'])
                        status = res.get('status')
                        pct_display = res.get('pct_display', 0)
                        presupuesto = res.get('presupuesto')
                        if status == 'over' and presupuesto:
                            messages.error(request, f"Atención: presupuesto para {presupuesto.categoria.nombre} ({presupuesto.mes}) alcanzado/sobrepasado ({pct_display}%).", extra_tags='transactions')
                        elif status == 'near' and presupuesto:
                            messages.warning(request, f"Cuidado: presupuesto para {presupuesto.categoria.nombre} ({presupuesto.mes}) cerca de llenarse ({pct_display}%).", extra_tags='transactions')
                except Exception:
                    pass
                return redirect('transactions:list')
            except Exception as e:
                messages.error(request, str(e), extra_tags='transactions')
    else:
        form = TransactionForm(usuario=profile)

    return render(request, 'transactions/form.html', {'form': form, 'editing': False})


@login_required
def transaction_edit(request, tipo, pk):
    '''Edita una transacción existente (ingreso o gasto)'''
    profile = Profile.objects.get(user=request.user)
    manager = TransactionManager(profile)

    # obtener datos iniciales
    if tipo == 'ingreso':
        trans = get_object_or_404(manager.usuario.ingreso_set.model, pk=pk, usuario=profile)
    else:
        trans = get_object_or_404(manager.usuario.gasto_set.model, pk=pk, usuario=profile)

    if request.method == 'POST':
        form = TransactionForm(request.POST, usuario=profile)
        if form.is_valid():
            try:
                manager.editar_transaccion(
                    tipo, 
                    pk,
                    form.cleaned_data['tipo'],
                    form.cleaned_data['categoria'].id,
                    form.cleaned_data['monto'],
                    form.cleaned_data['fecha'],
                    form.cleaned_data.get('descripcion', ''),
                )
                messages.success(request, 'Transacción actualizada.', extra_tags='transactions')
                # verificar presupuesto tras edición (si es gasto)
                try:
                    if form.cleaned_data['tipo'] == 'gasto':
                        res = _evaluate_budget_for_category_month(profile, form.cleaned_data['categoria'], form.cleaned_data['fecha'])
                        status = res.get('status')
                        pct_display = res.get('pct_display', 0)
                        presupuesto = res.get('presupuesto')
                        if status == 'over' and presupuesto:
                            messages.error(request, f"Atención: presupuesto para {presupuesto.categoria.nombre} ({presupuesto.mes}) alcanzado/sobrepasado ({pct_display}%).", extra_tags='transactions')
                        elif status == 'near' and presupuesto:
                            messages.warning(request, f"Cuidado: presupuesto para {presupuesto.categoria.nombre} ({presupuesto.mes}) cerca de llenarse ({pct_display}%).", extra_tags='transactions')
                except Exception:
                    pass
                return redirect('transactions:list')
            except Exception as e:
                messages.error(request, str(e), extra_tags='transactions')
    else:
        # initial para el formulario en con los datos a editar
        initial = {
            'tipo': tipo,
            'categoria': trans.categoria,
            'monto': trans.monto,
            'fecha': trans.fecha,
            'descripcion': trans.descripcion,
        }
        form = TransactionForm(initial=initial, usuario=profile)

    return render(request, 'transactions/form.html', {'form': form, 'editing': True})


@login_required
def transaction_delete(request, tipo, pk):
    '''Elimina una transacción (ingreso o gasto)'''
    
    profile = Profile.objects.get(user=request.user)
    manager = TransactionManager(profile)
    if request.method == 'POST':
        try:
            manager.eliminar_transaccion(tipo, pk)
            messages.success(request, 'Transacción eliminada.', extra_tags='transactions')
        except Exception as e:
            messages.error(request, str(e), extra_tags='transactions')
    return redirect('transactions:list')
from django.shortcuts import render

