from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category
from .forms import CategoryForm
from users.models import Profile
from .services.category_manager import CategoryManager

@login_required
def categories_list(request):
	profile = Profile.objects.get(user=request.user)
	manager = CategoryManager(profile)
	if request.method == 'POST' and 'create_category' in request.POST:
		form = CategoryForm(request.POST)
		if form.is_valid():
			try:
				manager.crear_categoria(
					form.cleaned_data['nombre'],
					form.cleaned_data['tipo'],
					form.cleaned_data.get('color') or None,
				)
				#extra_tags para mensajes específicos de categorías en los templates
				messages.success(request, 'Categoría creada correctamente.', extra_tags='categories')
				return redirect('categories:list') #volver a todas las categorias
			except ValueError as e:
				messages.error(request, str(e), extra_tags='categories')
	else:
		# Formulario en blanco para nueva categoría
		form = CategoryForm()

	categories = manager.obtener_categorias().order_by('nombre')
	return render(request, 'users/categories.html', {'form': form, 'categories': categories})


@login_required
def category_edit(request, pk):
	profile = Profile.objects.get(user=request.user)
	manager = CategoryManager(profile)
	# obtener id específico de la categoria a editar
	category = get_object_or_404(Category, pk=pk, usuario=profile)
	if request.method == 'POST':
		form = CategoryForm(request.POST, instance=category)
		if form.is_valid():
			try:
				manager.editar_categoria(pk, nuevo_nombre=form.cleaned_data['nombre'], nuevo_color=form.cleaned_data.get('color'), nuevo_tipo=form.cleaned_data.get('tipo'))
				messages.success(request, 'Categoría actualizada correctamente.', extra_tags='categories')
				return redirect('categories:list')
			except Category.DoesNotExist:
				messages.error(request, 'Categoría no encontrada.', extra_tags='categories')
			except ValueError as e:
				messages.error(request, str(e), extra_tags='categories')
	else:
		form = CategoryForm(instance=category)

	categories = manager.obtener_categorias().order_by('nombre')
	return render(request, 'users/categories.html', {'form': form, 'categories': categories, 'editing': True, 'editing_pk': pk})


@login_required
def category_delete(request, pk):
	profile = Profile.objects.get(user=request.user)
	manager = CategoryManager(profile)
	category = get_object_or_404(Category, pk=pk, usuario=profile)
	if request.method == 'POST':
		try:
			manager.eliminar_categoria(pk)
			messages.success(request, 'Categoría eliminada.', extra_tags='categories')
			return redirect('categories:list')
		except ValueError as e:
			messages.error(request, str(e), extra_tags='categories')
			return redirect('categories:list')
	return render(request, 'users/categories.html', {'categories': manager.obtener_categorias().order_by('nombre')})
