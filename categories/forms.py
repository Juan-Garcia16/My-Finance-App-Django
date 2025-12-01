from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    '''Formulario para crear/editar categorías en la aplicación por medio de una modal'''
    class Meta:
        model = Category
        fields = ['nombre', 'tipo', 'color']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 rounded-lg h-12 px-4',
                'placeholder': 'Ej: Comida, Transporte'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select flex w-full rounded-lg h-12 px-3'
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'h-12 w-12 p-0 border-0 bg-transparent'
            }),
        }
