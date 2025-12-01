from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from users.models import Profile
from categories.models import Category
from .forms import TransactionForm
from .services.transaction_manager import TransactionManager
from decimal import Decimal, ROUND_HALF_UP


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

