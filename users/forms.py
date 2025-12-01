from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

# Tipos de moneda disponibles (feature extensible), por el momento solo se usa COP
MONEDAS_CHOICES = [
    ('COP', 'COP - Peso colombiano'),
    ('USD', 'USD - Dólar estadounidense'),
    ('EUR', 'EUR - Euro'),
    ('MXN', 'MXN - Peso mexicano'),
    ('GBP', 'GBP - Libra esterlina'),
]

class UserRegisterForm(UserCreationForm):
    '''Formulario de registro de usuario que extiende UserCreationForm para incluir email, 
    moneda preferida y saldo inicial.'''
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
            'class': 'form-input flex w-full min-w-0 flex-1 rounded-lg h-12 px-3',
            'placeholder': 'tu.email@ejemplo.com'    
        }))

    moneda_preferida = forms.ChoiceField(choices=MONEDAS_CHOICES, widget=forms.Select(attrs={
            'class': 'form-select flex w-full rounded-lg h-12 px-3'
        }), initial='COP')
    
    saldo_inicial = forms.DecimalField(required=False, max_digits=12, decimal_places=2, initial=0, widget=forms.NumberInput(attrs={
            'class': 'form-input flex w-full rounded-r-lg h-12 px-3', 'placeholder': '0.00'
        }))


    # El Meta se usa para definir el modelo asociado y los campos a incluir en el formulario
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", 'moneda_preferida', 'saldo_inicial']

    def save(self, commit=True):
        """Guardar el usuario y crear o actualizar el perfil asociado."""
        # user usa super() para llamar al método save() del UserCreationForm
        user = super().save(commit=commit)
        # crear o actualizar el perfil asociado
        moneda = self.cleaned_data.get('moneda_preferida', 'COP')
        saldo = self.cleaned_data.get('saldo_inicial') or 0

        try:
            profile = Profile.objects.get(user=user)
            profile.moneda_preferida = moneda
            profile.saldo_inicial = saldo
            profile.saldo_actual = saldo
            profile.save()
        except Profile.DoesNotExist:
            # crear nuevo perfil si no existe
            Profile.objects.create(user=user, moneda_preferida=moneda, saldo_inicial=saldo, saldo_actual=saldo)
        return user
    
    # constructor para personalizar widgets
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


class UserUpdateForm(forms.ModelForm):
    '''Formulario para actualizar el usuario (username y email).'''
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input flex w-full min-w-0 flex-1 rounded-lg h-12 px-3',
        'placeholder': 'tu.email@ejemplo.com'
    }))

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input flex w-full min-w-0 flex-1 rounded-lg h-12 px-3',
            'placeholder': 'Nombre de usuario'
        })


class ProfileUpdateForm(forms.ModelForm):
    '''Formulario para actualizar el perfil (moneda preferida y saldo inicial).'''
    moneda_preferida = forms.ChoiceField(choices=MONEDAS_CHOICES, widget=forms.Select(attrs={'class': 'form-select flex w-full rounded-lg h-12 px-3'}))

    # campos a incluir en el formulario
    class Meta:
        model = Profile
        fields = ['moneda_preferida', 'saldo_inicial']
        widgets = {
            'saldo_inicial': forms.NumberInput(attrs={'class': 'form-input flex w-full rounded-lg h-12 pl-8', 'placeholder': '0.00'}),
        }

