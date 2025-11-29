from django.urls import path
from . import views

app_name = 'transactions'
urlpatterns = [
    path('', views.transactions_list, name='list'),
    path('create/', views.transactions_create, name='create'),
    path('edit/<str:tipo>/<int:pk>/', views.transaction_edit, name='edit'),
    path('delete/<str:tipo>/<int:pk>/', views.transaction_delete, name='delete'),
]