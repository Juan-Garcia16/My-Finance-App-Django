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

	# Redondear a pesos enteros
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

	# Reemplazar comas por puntos para formato COP
	return s.replace(',', '.')


def build_daily_series(profile, year, month):
	"""Construye las series diarias para el gráfico del dashboard.

	Devuelve una tupla (labels, ingresos_by_day, gastos_by_day) donde:
	- labels: lista de strings con los días del mes ('01', '02', ...)
	- ingresos_by_day: lista de floats con la suma de ingresos por día
	- gastos_by_day: lista de floats con la suma de gastos por día

	La función es defensiva: ignora transacciones con datos inválidos en la fecha
	o monto para no romper la generación del gráfico.
	"""
	# Número de días del mes
	days_in_month = calendar.monthrange(year, month)[1]
	labels = [f"{d:02d}" for d in range(1, days_in_month + 1)]

	ingresos_by_day = [0.0] * days_in_month
	gastos_by_day = [0.0] * days_in_month

	ingresos_days_qs = Ingreso.objects.filter(usuario=profile, fecha__year=year, fecha__month=month)
	for inc in ingresos_days_qs:
		try:
			day = inc.fecha.day
			ingresos_by_day[day - 1] += float(inc.monto or 0)
		except Exception:
			continue

	gastos_days_qs = Gasto.objects.filter(usuario=profile, fecha__year=year, fecha__month=month)
	for g in gastos_days_qs:
		try:
			day = g.fecha.day
			gastos_by_day[day - 1] += float(g.monto or 0)
		except Exception:
			continue

	return labels, ingresos_by_day, gastos_by_day


def build_recent_transactions(profile, limit=5):
	"""Recupera y normaliza las últimas transacciones (ingresos + gastos)"""
	ingresos_qs = Ingreso.objects.filter(usuario=profile).values(
		'id', 'categoria__nombre', 'categoria__color', 'monto', 'fecha', 'descripcion'
	)
	gastos_qs = Gasto.objects.filter(usuario=profile).values(
		'id', 'categoria__nombre', 'categoria__color', 'monto', 'fecha', 'descripcion'
	)

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

	# ordenar por fecha (y luego id) descendente y limitar
	recent_sorted = sorted(recent, key=lambda r: (r['fecha'], r['id']), reverse=True)
	return recent_sorted[:limit]

# Vista para logeo de usuarios
class CustomLoginView(LoginView):
	template_name = 'users/login.html'

# Vista para logout de usuarios
class CustomLogoutView(LogoutView):
	next_page = reverse_lazy('users:login')

# Vista para registro de nuevos usuarios
def register_view(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			user = form.save()
			# Logear de forma automática al registrarse
			login(request, user)
			return redirect('users:dashboard')
	else:
		# Mostrar formulario vacío para registro
		form = UserRegisterForm()
	return render(request, 'users/register.html', {'form': form})


# Vista principal del dashboard
@login_required
def dashboard_view(request):
    # Asegurar que el perfil exista y obtener sus datos
	profile, created = Profile.objects.get_or_create(
		user=request.user,
		defaults={
			'moneda_preferida': 'COP',
			'saldo_inicial': 0,
			'saldo_actual': 0,
		}
	)
	
	# Variables para el contexto de analisis y registro mensual de los datos
	now = timezone.now()
	year = now.year
	month = now.month

	# ingresos y gastos totales del mes actual
	ingresos_agg = Ingreso.objects.filter(usuario=profile, fecha__year=year, fecha__month=month).aggregate(total=Sum('monto'))
	gastos_agg = Gasto.objects.filter(usuario=profile, fecha__year=year, fecha__month=month).aggregate(total=Sum('monto'))

	# ingresos y gastos totales como Decimals
	ingresos_total = ingresos_agg['total'] or Decimal('0.00')
	gastos_total = gastos_agg['total'] or Decimal('0.00')

	# preparar contexto para render
	context = {
		'profile': profile,
		'ingresos_mes': ingresos_total,
		'gastos_mes': gastos_total,
		# Valores formateados a COP 
		'saldo_actual_display': format_cop(profile.saldo_actual),
		'ingresos_mes_display': format_cop(ingresos_total),
		'gastos_mes_display': format_cop(gastos_total),
	}

    # Series diarias para el gráfico 
    # Número de días del mes (ej. 30/31/28)
	labels, ingresos_by_day, gastos_by_day = build_daily_series(profile, year, month)
 
	# Preparar JSON para el frontend (Chart.js)
	context['chart_labels_json'] = json.dumps(labels)
	context['ingresos_data_json'] = json.dumps(ingresos_by_day)
	context['gastos_data_json'] = json.dumps(gastos_by_day)
 
 
	# Últimas transacciones para vista en el dashboard
	context['recent_transactions'] = build_recent_transactions(profile, limit=5)

	return render(request, 'dashboard.html', context)

@login_required
def profile_view(request):
	'''Vista para ver y actualizar el perfil del usuario.'''
	# asegurar existencia
	profile, created = Profile.objects.get_or_create(
		user=request.user,
		defaults={
			'moneda_preferida': 'COP',
			'saldo_inicial': 0,
			'saldo_actual': 0,
		}
	)

	if request.method == 'POST':
		# user form de django y profile form de la palicacion
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
		# forms con datos iniciales
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=profile)

	return render(request, 'users/profile.html', {'u_form': u_form, 'p_form': p_form, 'profile': profile})
