"""
apps/core/forms.py
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Departamento, Cargo


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Utilizador',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de utilizador'})
    )
    password = forms.CharField(
        label='Palavra-passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Palavra-passe'})
    )


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'departamento', 'cargo', 'telefone', 'is_superuser', 'ativo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'departamento', 'cargo', 'telefone', 'foto', 'ativo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
