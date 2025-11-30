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


@login_required
def list_goals(request):
    profile = Profile.objects.get(user=request.user)
    goals = MetaAhorro.objects.filter(usuario=profile).order_by('fecha_limite')
    contribution_form = ContributionForm()
    from .forms import GoalForm
    goal_form = GoalForm()
    return render(request, 'goals/goals.html', {
        'goals': goals,
        'contribution_form': contribution_form,
        'goal_form': goal_form,
    })


@login_required
def create_goal(request):
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
            'action': f"{request.scheme}://{request.get_host()}/goals/{goal.id}/edit/",
        }
        return JsonResponse(data)

    return render(request, 'goals/form.html', {'form': form, 'create': False, 'goal': goal})


@login_required
def delete_goal(request, pk):
    profile = Profile.objects.get(user=request.user)
    goal = get_object_or_404(MetaAhorro, pk=pk, usuario=profile)
    # Usar confirm del navegador; no renderizamos plantilla GET.
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Meta eliminada.', extra_tags='goals')
        return redirect('goals:list')
    # Si se accede por GET redirigimos a la lista (evitamos la plantilla de confirmación)
    return redirect('goals:list')


@login_required
def add_contribution(request, pk):
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
                manager.añadir_progreso(goal.id, monto)
                messages.success(request, 'Aporte agregado a la meta.', extra_tags='goals')
        else:
            messages.error(request, 'El monto no es válido.', extra_tags='goals')
    return redirect('goals:list')


@login_required
def recalculate_progress_from_transactions(request):
    """
    Recalcula el progreso de todas las metas del usuario basándose en las transacciones.
    Convención: si la descripción de un `Ingreso` contiene `meta:<id>` (por ejemplo `meta:3`),
    ese ingreso se suma al progreso de la meta con id=3.
    Esta vista es idempotente y puede usarse como utilidad administrativa por el usuario.
    """
    profile = Profile.objects.get(user=request.user)
    goals = MetaAhorro.objects.filter(usuario=profile)

    # Inicializamos conteo
    from decimal import Decimal
    sums = {g.id: Decimal('0') for g in goals}

    ingresos = Ingreso.objects.filter(usuario=profile)
    pattern = re.compile(r"meta:(\d+)")
    for ing in ingresos:
        if not ing.descripcion:
            continue
        matches = pattern.findall(ing.descripcion)
        for mid in matches:
            try:
                mid_i = int(mid)
            except ValueError:
                continue
            if mid_i in sums:
                try:
                    sums[mid_i] += Decimal(ing.monto)
                except Exception:
                    sums[mid_i] += Decimal(str(ing.monto))

    # Guardar valores calculados (capping en monto_objetivo)
    for g in goals:
        calc = sums.get(g.id, Decimal('0'))
        if g.monto_objetivo and calc >= g.monto_objetivo:
            g.progreso = g.monto_objetivo
        else:
            g.progreso = calc
        g.save()

    messages.success(request, 'Progreso recalculado desde transacciones.', extra_tags='goals')
    return redirect('goals:list')
    
