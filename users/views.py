from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserRegisterForm
from django.urls import reverse_lazy
from .models import Profile


class CustomLoginView(LoginView):
	template_name = 'login.html'


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
	return render(request, 'register.html', {'form': form})


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
	return render(request, 'dashboard.html', {'profile': profile})
