from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input flex w-full min-w-0 flex-1 rounded-lg h-12 px-3',
        'placeholder': 'tu.email@ejemplo.com'
    }))

    moneda_preferida = forms.ChoiceField(choices=[
        ('COP', 'COP - Peso colombiano'),
        ('USD', 'USD - Dólar estadounidense'),
        ('EUR', 'EUR - Euro'),
        ('MXN', 'MXN - Peso mexicano'),
        ('GBP', 'GBP - Libra esterlina'),
    ], widget=forms.Select(attrs={'class': 'form-select flex w-full rounded-lg h-12 px-3'}), initial='COP')

    saldo_inicial = forms.DecimalField(required=False, max_digits=12, decimal_places=2, initial=0,
                                       widget=forms.NumberInput(attrs={'class': 'form-input flex w-full rounded-lg h-12 px-3', 'placeholder': '0.00'}))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", 'moneda_preferida', 'saldo_inicial']

    def save(self, commit=True):
        user = super().save(commit=commit)
        # create or update profile
        moneda = self.cleaned_data.get('moneda_preferida', 'COP')
        saldo = self.cleaned_data.get('saldo_inicial') or 0
        # Import Profile here to avoid circular imports
        try:
            profile = Profile.objects.get(user=user)
            profile.moneda_preferida = moneda
            profile.saldo_inicial = saldo
            profile.saldo_actual = saldo
            profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(user=user, moneda_preferida=moneda, saldo_inicial=saldo, saldo_actual=saldo)
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # apply Tailwind classes to inherited fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-input flex w-full min-w-0 flex-1 rounded-lg h-12 px-3',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input flex w-full min-w-0 flex-1 rounded-lg h-12 px-3',
            'placeholder': 'Crea una contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input flex w-full min-w-0 flex-1 rounded-lg h-12 px-3',
            'placeholder': 'Confirma la contraseña'
        })
