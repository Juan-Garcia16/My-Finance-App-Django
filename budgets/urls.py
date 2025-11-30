from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
	path('', views.budgets_list, name='list'),
	path('delete/<int:pk>/', views.delete_budget, name='delete'),
	path('edit/<int:pk>/', views.edit_budget, name='edit'),
]