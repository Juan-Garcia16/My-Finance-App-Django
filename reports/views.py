from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .services.report_manager import ReportManager
import json
from django.db.models import Sum
from transactions.models import Ingreso, Gasto


@login_required
def reports_index(request):
	profile = request.user.profile
	rm = ReportManager(profile)

	# Overall ingresos vs gastos for current month
	now = timezone.now()
	year = now.year
	month = now.month

	ingresos_agg = Ingreso.objects.filter(usuario=profile, fecha__year=year, fecha__month=month).aggregate(total=Sum('monto'))
	gastos_agg = Gasto.objects.filter(usuario=profile, fecha__year=year, fecha__month=month).aggregate(total=Sum('monto'))

	ingresos_total = float(ingresos_agg.get('total') or 0)
	gastos_total = float(gastos_agg.get('total') or 0)

	# net savings for the month
	neto = ingresos_total - gastos_total

	# gastos por categoria for current month
	gastos_cat_qs = list(
		Gasto.objects.filter(usuario=profile, fecha__year=year, fecha__month=month)
		.values('categoria__nombre')
		.annotate(total=Sum('monto'))
	)
	cat_labels = [c['categoria__nombre'] for c in gastos_cat_qs]
	cat_values = [float(c['total'] or 0) for c in gastos_cat_qs]

	# ingresos por categoria for current month
	ingresos_cat_qs = list(
		Ingreso.objects.filter(usuario=profile, fecha__year=year, fecha__month=month)
		.values('categoria__nombre')
		.annotate(total=Sum('monto'))
	)
	ing_labels = [c['categoria__nombre'] for c in ingresos_cat_qs]
	ing_values = [float(c['total'] or 0) for c in ingresos_cat_qs]

	# presupuestos y metas (build lightweight dicts for template)
	now = timezone.now()
	mes_key = f"{now.year}-{now.month:02d}"
	presupuestos_qs = rm.estado_presupuestos().filter(mes=mes_key)
	presupuestos = []
	for p in presupuestos_qs:
		lim = float(p.limite or 0)
		gasto = float(p.gasto_actual or 0)
		pct = 0
		state = 'ok'
		if lim > 0:
			pct = int(round((gasto / lim) * 100))
			if gasto >= lim:
				state = 'exceeded'
			elif gasto >= lim * 0.8:
				state = 'warning'
		presupuestos.append({
			'categoria_nombre': p.categoria.nombre,
			'mes': p.mes,
			'limite': lim,
			'gasto_actual': gasto,
			'pct': pct,
			'state': state,
		})

	metas_qs = rm.estado_metas()
	metas = list(metas_qs)

	context = {
		'cat_labels_json': json.dumps(cat_labels),
		'cat_values_json': json.dumps(cat_values),
		'ingresos_total': ingresos_total,
		'gastos_total': gastos_total,
		'neto': neto,
		'ingresos_cat_labels_json': json.dumps(ing_labels),
		'ingresos_cat_values_json': json.dumps(ing_values),
		'presupuestos': presupuestos,
		'metas': metas,
	}
	return render(request, 'reports/reports.html', context)
