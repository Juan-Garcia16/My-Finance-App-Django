from django import forms
from .models import Presupuesto
from categories.models import Category


class BudgetForm(forms.ModelForm):
    # Use HTML month input to get YYYY-MM value
    mes = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'month', 'class': 'border rounded px-2 py-1'}),
        label='Mes (YYYY-MM)'
    )

    class Meta:
        model = Presupuesto
        fields = ['categoria', 'mes', 'limite']
        widgets = {
            'limite': forms.NumberInput(attrs={'step': '0.01', 'class': 'border rounded px-2 py-1'}),
            'categoria': forms.Select(attrs={'class': 'border rounded px-2 py-1'})
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario is not None:
            # limitar categorías al usuario
            self.fields['categoria'].queryset = Category.objects.filter(usuario=usuario)

    def clean_mes(self):
        mes = self.cleaned_data['mes']
        # esperar formato 'YYYY-MM'
        if not isinstance(mes, str) or len(mes) < 7 or '-' not in mes:
            raise forms.ValidationError('Formato de mes inválido. Usa YYYY-MM.')
        return mes
