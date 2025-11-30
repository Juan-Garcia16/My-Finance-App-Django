from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserRegisterForm
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Profile
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
import calendar
import json
from transactions.models import Ingreso, Gasto
from decimal import ROUND_HALF_UP


def format_cop(value):
	"""Format a numeric/Decimal value as Colombian pesos display (no cents).

	Examples:
		Decimal('1100000.00') -> '1.100.000'
	"""
	if value is None:
		return ''
	try:
		amt = Decimal(value)
	except Exception:
		try:
			amt = Decimal(str(value))
		except Exception:
			return str(value)

	# Round to whole pesos
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


class CustomLoginView(LoginView):
	template_name = 'users/login.html'


class CustomLogoutView(LogoutView):
	next_page = reverse_lazy('users:login')


def register_view(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			user = form.save()
			# Optionally create Profile via signal or here if desired
			login(request, user)
			return redirect('users:dashboard')
	else:
		form = UserRegisterForm()
	return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard_view(request):
	# You can add context data (balances, transactions) here
	# Ensure the user has a Profile (create default if missing)
	profile, created = Profile.objects.get_or_create(
		user=request.user,
		defaults={
			'moneda_preferida': 'COP',
			'saldo_inicial': 0,
			'saldo_actual': 0,
		}
	)
	# calcular totales del mes actual
	now = timezone.now()
	year = now.year
	month = now.month

	ingresos_agg = Ingreso.objects.filter(usuario=profile, fecha__year=year, fecha__month=month).aggregate(total=Sum('monto'))
	gastos_agg = Gasto.objects.filter(usuario=profile, fecha__year=year, fecha__month=month).aggregate(total=Sum('monto'))

	ingresos_total = ingresos_agg['total'] or Decimal('0.00')
	gastos_total = gastos_agg['total'] or Decimal('0.00')

	context = {
		'profile': profile,
		'ingresos_mes': ingresos_total,
		'gastos_mes': gastos_total,
		# display versions (formatted as COP)
		'saldo_actual_display': format_cop(profile.saldo_actual),
		'ingresos_mes_display': format_cop(ingresos_total),
		'gastos_mes_display': format_cop(gastos_total),
	}

	# build daily series for current month (labels: days)
	# days count
	days_in_month = calendar.monthrange(year, month)[1]
	labels = [f"{d:02d}" for d in range(1, days_in_month + 1)]

	# initialize zeros
	ingresos_by_day = [0.0] * days_in_month
	gastos_by_day = [0.0] * days_in_month

	# aggregate ingresos by day
	ingresos_days_qs = Ingreso.objects.filter(usuario=profile, fecha__year=year, fecha__month=month)
	for inc in ingresos_days_qs:
		try:
			day = inc.fecha.day
			ingresos_by_day[day-1] += float(inc.monto or 0)
		except Exception:
			continue

	# aggregate gastos by day
	gastos_days_qs = Gasto.objects.filter(usuario=profile, fecha__year=year, fecha__month=month)
	for g in gastos_days_qs:
		try:
			day = g.fecha.day
			gastos_by_day[day-1] += float(g.monto or 0)
		except Exception:
			continue

	# prepare JSON for template
	context['chart_labels_json'] = json.dumps(labels)
	context['ingresos_data_json'] = json.dumps(ingresos_by_day)
	context['gastos_data_json'] = json.dumps(gastos_by_day)
	# Obtener últimas transacciones (ingresos + gastos) y ordenar por fecha descendente
	# incluimos el color de la categoría para mostrarlo en el dashboard
	ingresos_qs = Ingreso.objects.filter(usuario=profile).values('id', 'categoria__nombre', 'categoria__color', 'monto', 'fecha', 'descripcion')
	gastos_qs = Gasto.objects.filter(usuario=profile).values('id', 'categoria__nombre', 'categoria__color', 'monto', 'fecha', 'descripcion')

	recent = []
	for i in ingresos_qs:
		recent.append({
			'id': i['id'],
			'tipo': 'ingreso',
			'categoria': i.get('categoria__nombre') or '',
			'categoria_color': i.get('categoria__color') or '#e5e7eb',
			'monto': i.get('monto') or Decimal('0.00'),
			'monto_display': format_cop(i.get('monto') or Decimal('0.00')),
			'fecha': i.get('fecha'),
			'descripcion': i.get('descripcion') or '',
		})
	for g in gastos_qs:
		recent.append({
			'id': g['id'],
			'tipo': 'gasto',
			'categoria': g.get('categoria__nombre') or '',
			'categoria_color': g.get('categoria__color') or '#e5e7eb',
			'monto': g.get('monto') or Decimal('0.00'),
			'monto_display': format_cop(g.get('monto') or Decimal('0.00')),
			'fecha': g.get('fecha'),
			'descripcion': g.get('descripcion') or '',
		})

	# ordenar por fecha (y luego id) descendente
	recent_sorted = sorted(recent, key=lambda r: (r['fecha'], r['id']), reverse=True)
	recent_top5 = recent_sorted[:5]

	context['recent_transactions'] = recent_top5

	return render(request, 'dashboard.html', context)

@login_required
def profile_view(request):
	# Ensure profile exists
	profile, created = Profile.objects.get_or_create(
		user=request.user,
		defaults={
			'moneda_preferida': 'COP',
			'saldo_inicial': 0,
			'saldo_actual': 0,
		}
	)

	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST, instance=profile)
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			messages.success(request, 'Perfil actualizado correctamente.')
			return redirect('users:profile')
		else:
			messages.error(request, 'Por favor corrige los errores en el formulario.')
	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=profile)

	return render(request, 'users/profile.html', {'u_form': u_form, 'p_form': p_form, 'profile': profile})
