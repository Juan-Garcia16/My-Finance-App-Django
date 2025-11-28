from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Category
from .forms import CategoryForm
from users.models import Profile


@login_required
def categories_list(request):
	profile = Profile.objects.get(user=request.user)
	if request.method == 'POST' and 'create_category' in request.POST:
		form = CategoryForm(request.POST)
		if form.is_valid():
			cat = form.save(commit=False)
			cat.usuario = profile
			cat.save()
			messages.success(request, 'Categoría creada correctamente.', extra_tags='categories')
			return redirect('categories:list')
	else:
		form = CategoryForm()

	categories = Category.objects.filter(usuario=profile).order_by('nombre')
	return render(request, 'users/categories.html', {'form': form, 'categories': categories})


@login_required
def category_edit(request, pk):
	profile = Profile.objects.get(user=request.user)
	category = get_object_or_404(Category, pk=pk, usuario=profile)
	if request.method == 'POST':
		form = CategoryForm(request.POST, instance=category)
		if form.is_valid():
			form.save()
			messages.success(request, 'Categoría actualizada correctamente.', extra_tags='categories')
			return redirect('categories:list')
	else:
		form = CategoryForm(instance=category)

	categories = Category.objects.filter(usuario=profile).order_by('nombre')
	return render(request, 'users/categories.html', {'form': form, 'categories': categories, 'editing': True, 'editing_pk': pk})


@login_required
def category_delete(request, pk):
	profile = Profile.objects.get(user=request.user)
	category = get_object_or_404(Category, pk=pk, usuario=profile)
	if request.method == 'POST':
		category.delete()
		messages.success(request, 'Categoría eliminada.', extra_tags='categories')
		return redirect('categories:list')
	return render(request, 'users/categories.html', {'categories': Category.objects.filter(usuario=profile).order_by('nombre')})
