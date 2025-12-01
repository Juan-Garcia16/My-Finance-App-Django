from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
	path('', views.categories_list, name='list'),
	# rutas para actuar entre n objetos Category
	path('edit/<int:pk>/', views.category_edit, name='edit'),
	path('delete/<int:pk>/', views.category_delete, name='delete'),
]
