from django import forms
from decimal import Decimal
from categories.models import Category

TIPO_CHOICES = [
    ("ingreso", "Ingreso"),
    ("gasto", "Gasto"),
]


class TransactionForm(forms.Form):
    shared_input_classes = 'block w-full rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-background-dark text-text-main dark:text-text-main-dark px-3 py-2'

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': shared_input_classes})
    )
    categoria = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        widget=forms.Select(attrs={'class': shared_input_classes})
    )
    monto = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': shared_input_classes,
            'placeholder': '0.00',
            'inputmode': 'decimal',
        })
    )
    fecha = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'class': shared_input_classes,
    }))
    descripcion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': f'{shared_input_classes} h-28 resize-none',
            'placeholder': 'Opcional: añade una nota breve',
        })
    )

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario is not None:
            self.fields['categoria'].queryset = Category.objects.filter(usuario=usuario).order_by('nombre')
