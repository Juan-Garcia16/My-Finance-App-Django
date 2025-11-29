from django import forms
from decimal import Decimal
from categories.models import Category

TIPO_CHOICES = [
    ("ingreso", "Ingreso"),
    ("gasto", "Gasto"),
]


class TransactionForm(forms.Form):
    tipo = forms.ChoiceField(choices=TIPO_CHOICES)
    categoria = forms.ModelChoiceField(queryset=Category.objects.none())
    monto = forms.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    descripcion = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':2}))

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario is not None:
            self.fields['categoria'].queryset = Category.objects.filter(usuario=usuario).order_by('nombre')
