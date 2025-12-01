from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import BudgetForm
from .models import Presupuesto

#Lista todos los presupuestos del usuario y permite crear nuevos
def budgets_list(request):
	profile = request.user.profile
 
	if request.method == 'POST':
		form = BudgetForm(request.POST, usuario=profile)
		if form.is_valid():
			categoria = form.cleaned_data['categoria']
			mes = form.cleaned_data['mes']
			limite = form.cleaned_data['limite']
			# crear presupuesto si no existe para la categoria+mes
			presupuesto, created = Presupuesto.objects.get_or_create(
				usuario=profile,
				categoria=categoria,
				mes=mes,
				defaults={'limite': limite}
			)
			if not created:
				presupuesto.limite = limite
				presupuesto.save()
				messages.success(request, 'Presupuesto actualizado correctamente.', extra_tags='budgets')
			else:
				messages.success(request, 'Presupuesto creado correctamente.', extra_tags='budgets')
			return redirect(reverse('budgets:list'))
		else:
			# render con errors y abrir modal en template
			budgets = Presupuesto.objects.filter(usuario=profile).select_related('categoria').order_by('-mes', '-pk')
			
            # calcular estado
			for p in budgets:
				try:
					p.porcentaje = float(p.gasto_actual) / float(p.limite) * 100 if p.limite and p.limite != 0 else 0
				except Exception:
					p.porcentaje = 0
				p.estado = 'ok'
				if p.porcentaje >= 100:
					p.estado = 'exceeded'
				elif p.porcentaje >= 80:
					p.estado = 'warning'
			return render(request, 'budgets/budgets.html', {'budgets': budgets, 'form': form, 'open_modal': True})

	# GET
	form = BudgetForm(usuario=request.user.profile)
	budgets = Presupuesto.objects.filter(usuario=profile).select_related('categoria').order_by('-mes', '-pk')
	exceeded_names = []
	for p in budgets:
		try:
			p.porcentaje = float(p.gasto_actual) / float(p.limite) * 100 if p.limite and p.limite != 0 else 0
		except Exception:
			p.porcentaje = 0
		p.estado = 'ok'
		if p.porcentaje >= 100:
			p.estado = 'exceeded'
			exceeded_names.append(p.categoria.nombre + ' (' + p.mes + ')')
		elif p.porcentaje >= 80:
			p.estado = 'warning'

	if exceeded_names:
		messages.warning(request, 'Se han superado los límites en: ' + ', '.join(exceeded_names), extra_tags='budgets')

	return render(request, 'budgets/budgets.html', {'budgets': budgets, 'form': form})


def delete_budget(request, pk):
	profile = request.user.profile
	presupuesto = get_object_or_404(Presupuesto, pk=pk, usuario=profile)
	if request.method == 'POST':
		presupuesto.delete()
		messages.success(request, 'Presupuesto eliminado.', extra_tags='budgets')
		return redirect(reverse('budgets:list'))

	return redirect(reverse('budgets:list'))


def edit_budget(request, pk):
	profile = request.user.profile
	presupuesto = get_object_or_404(Presupuesto, pk=pk, usuario=profile)
	if request.method == 'POST':
		form = BudgetForm(request.POST, instance=presupuesto, usuario=profile)
		if form.is_valid():
			form.save()
			messages.success(request, 'Presupuesto actualizado.', extra_tags='budgets')
			return redirect(reverse('budgets:list'))
		else:
			#  renderizar mismo template con modal abierta y errores
			budgets = Presupuesto.objects.filter(usuario=profile).select_related('categoria').order_by('-mes', '-pk')
			for p in budgets:
				try:
					p.porcentaje = float(p.gasto_actual) / float(p.limite) * 100 if p.limite and p.limite != 0 else 0
				except Exception:
					p.porcentaje = 0
				p.estado = 'ok'
				if p.porcentaje >= 100:
					p.estado = 'exceeded'
				elif p.porcentaje >= 80:
					p.estado = 'warning'
			return render(request, 'budgets/budgets.html', {'budgets': budgets, 'form': form, 'open_modal': True, 'edit_pk': pk})
	else:
		form = BudgetForm(instance=presupuesto, usuario=profile)
		budgets = Presupuesto.objects.filter(usuario=profile).select_related('categoria').order_by('-mes', '-pk')
		for p in budgets:
			try:
				p.porcentaje = float(p.gasto_actual) / float(p.limite) * 100 if p.limite and p.limite != 0 else 0
			except Exception:
				p.porcentaje = 0
			p.estado = 'ok'
			if p.porcentaje >= 100:
				p.estado = 'exceeded'
			elif p.porcentaje >= 80:
				p.estado = 'warning'
		return render(request, 'budgets/budgets.html', {'budgets': budgets, 'form': form, 'open_modal': True, 'edit_pk': pk})

