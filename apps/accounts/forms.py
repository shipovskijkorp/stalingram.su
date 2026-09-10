from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class IdentifierAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин или почта",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "autofocus": True,
                "placeholder": "Логин или почта",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "placeholder": "Пароль"}
        ),
    )


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Логин",
        max_length=150,
        widget=forms.TextInput(
            attrs={"autocomplete": "username", "placeholder": "Логин"}
        ),
    )
    email = forms.EmailField(
        label="Почта",
        widget=forms.EmailInput(
            attrs={"autocomplete": "email", "placeholder": "name@example.com"}
        ),
    )
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "Пароль"}
        ),
    )
    password2 = forms.CharField(
        label="Повтор пароля",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "Повторите пароль"}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Пользователь с таким логином уже существует.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Эта почта уже используется.")
        return email
