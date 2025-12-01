from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Profile
from .models import MetaAhorro
from decimal import Decimal
from .forms import GoalForm, ContributionForm
from .services.goal_manager import GoalManager
from transactions.models import Ingreso
import re
from django.http import JsonResponse

from decimal import ROUND_HALF_UP


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
def list_goals(request):
    '''Lista todas las metas de ahorro del usuario'''
    profile = Profile.objects.get(user=request.user)
    goals = MetaAhorro.objects.filter(usuario=profile).order_by('fecha_limite')
    contribution_form = ContributionForm()
    goal_form = GoalForm()

    # formateo a COP para cada monto de la meta
    for g in goals:
        try:
            g.progreso_display = _format_cop(g.progreso)
        except Exception:
            g.progreso_display = str(g.progreso)
        try:
            g.monto_objetivo_display = _format_cop(g.monto_objetivo)
        except Exception:
            g.monto_objetivo_display = str(g.monto_objetivo)
    return render(request, 'goals/goals.html', {
        'goals': goals,
        'contribution_form': contribution_form,
        'goal_form': goal_form,
    })


@login_required
def create_goal(request):
    '''Crea una nueva meta de ahorro'''
    
    profile = Profile.objects.get(user=request.user)
    manager = GoalManager(profile)
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            manager.crear_meta(cd['nombre'], cd['monto_objetivo'], cd['fecha_limite'])
            messages.success(request, 'Meta creada correctamente.', extra_tags='goals')
            return redirect('goals:list')
    else:
        form = GoalForm()
    return render(request, 'goals/form.html', {'form': form, 'create': True})


@login_required
def edit_goal(request, pk):
    '''Edita una meta de ahorro existente'''
    
    profile = Profile.objects.get(user=request.user)
    goal = get_object_or_404(MetaAhorro, pk=pk, usuario=profile)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meta actualizada.', extra_tags='goals')
            return redirect('goals:list')
    else:
        form = GoalForm(instance=goal)
        
    # Si se solicita partial=1 devolvemos JSON con los datos de la meta (para rellenar el form inline)
    if request.GET.get('partial') == '1':
        data = {
            'id': goal.id,
            'nombre': goal.nombre,
            'monto_objetivo': str(goal.monto_objetivo),
            'fecha_limite': goal.fecha_limite.isoformat() if goal.fecha_limite else '',
            # action URL para el formulario
            'action': f"{request.scheme}://{request.get_host()}/goals/{goal.id}/edit/",
        }
        return JsonResponse(data)

    return render(request, 'goals/form.html', {'form': form, 'create': False, 'goal': goal})


@login_required
def delete_goal(request, pk):
    '''Elimina una meta de ahorro'''
    
    profile = Profile.objects.get(user=request.user)
    goal = get_object_or_404(MetaAhorro, pk=pk, usuario=profile)

    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Meta eliminada.', extra_tags='goals')
        return redirect('goals:list')
    # Si se accede por GET redirigimos a la lista (evitamos la plantilla de confirmación)
    return redirect('goals:list')


@login_required
def add_contribution(request, pk):
    '''Anade una contribución a una meta de ahorro'''
    
    profile = Profile.objects.get(user=request.user)
    goal = get_object_or_404(MetaAhorro, pk=pk, usuario=profile)
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            monto = form.cleaned_data['monto']
            # Evitar que se aporte más si ya alcanzó el objetivo
            if goal.progreso >= goal.monto_objetivo:
                messages.info(request, 'La meta ya está cumplida.', extra_tags='goals')
            else:
                manager = GoalManager(profile)
                manager.anadir_progreso(goal.id, monto)
                messages.success(request, 'Aporte agregado a la meta.', extra_tags='goals')
        else:
            messages.error(request, 'El monto no es válido.', extra_tags='goals')
    return redirect('goals:list')