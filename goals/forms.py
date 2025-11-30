from django import forms
from .models import MetaAhorro


class GoalForm(forms.ModelForm):
    fecha_limite = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border p-2"})
    )

    class Meta:
        model = MetaAhorro
        fields = ["nombre", "monto_objetivo", "fecha_limite"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "w-full rounded-md border p-2"}),
            "monto_objetivo": forms.NumberInput(attrs={"class": "w-full rounded-md border p-2", "step": "0.01"}),
        }


class ContributionForm(forms.Form):
    monto = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01,
                               widget=forms.NumberInput(attrs={"class": "w-24 rounded-md border p-2", "step": "0.01"}))
