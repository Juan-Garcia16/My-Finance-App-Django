from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
	path('', views.list_goals, name='list'),
	path('create/', views.create_goal, name='create'),
	path('<int:pk>/edit/', views.edit_goal, name='edit'),
	path('<int:pk>/delete/', views.delete_goal, name='delete'),
	path('<int:pk>/contribute/', views.add_contribution, name='contribute'),

]