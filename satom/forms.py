from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class GuessForm(forms.Form):
    guess = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control col-sm-4",
            "placeholder": "Proposition",
            "maxlength": 50,
            "minlength": 0,
            "autocomplete": "off",
            "autofocus": "on",
        })
    )

    def __init__(self, longueur):
        super().__init__()
        self.fields['guess'].widget.attrs.update({
            "maxlength": longueur,
            "minlength": longueur,
        })


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            "placeholder": "Entrez votre nom d'utilisateur",
            "class": "form-control"
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Entrez votre mot de passe",
            "class": "form-control"
        })
    )

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            "placeholder": "Votre nom d'utilisateur",
            "class": "form-control"
        })
    )
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Mot de passe",
            "class": "form-control"
        })
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirmez le mot de passe",
            "class": "form-control"
        })
    )

    class Meta:
        model = User
        fields = ["username"]
