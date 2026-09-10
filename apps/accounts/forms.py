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
        if User.objects.filter(email__iexact=username).exists():
            raise forms.ValidationError("Этот логин совпадает с почтой другого пользователя.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Эта почта уже используется.")
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("Эта почта совпадает с логином другого пользователя.")
        return email


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Имя",
        required=False,
        max_length=150,
        widget=forms.TextInput(
            attrs={"autocomplete": "given-name", "placeholder": "Имя"}
        ),
    )
    last_name = forms.CharField(
        label="Фамилия",
        required=False,
        max_length=150,
        widget=forms.TextInput(
            attrs={"autocomplete": "family-name", "placeholder": "Фамилия"}
        ),
    )
    username = forms.CharField(
        label="Имя пользователя",
        max_length=150,
        widget=forms.TextInput(
            attrs={"autocomplete": "username", "placeholder": "username"}
        ),
    )
    bio = forms.CharField(
        label="О себе",
        required=False,
        max_length=160,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "maxlength": 160,
                "placeholder": "Несколько слов о себе",
            }
        ),
    )
    email = forms.EmailField(
        label="Почта",
        widget=forms.EmailInput(
            attrs={"autocomplete": "email", "placeholder": "name@example.com"}
        ),
    )
    avatar = forms.ImageField(
        label="Фотография профиля",
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/png,image/jpeg,image/webp"}),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "bio", "email", "avatar")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        users = User.objects.exclude(pk=self.instance.pk)
        if users.filter(username__iexact=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        if users.filter(email__iexact=username).exists():
            raise forms.ValidationError("Это имя совпадает с почтой другого пользователя.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        users = User.objects.exclude(pk=self.instance.pk)
        if users.filter(email__iexact=email).exists():
            raise forms.ValidationError("Эта почта уже используется.")
        if users.filter(username__iexact=email).exists():
            raise forms.ValidationError("Эта почта совпадает с именем другого пользователя.")
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if not avatar:
            return avatar

        if getattr(avatar, "size", 0) > 5 * 1024 * 1024:
            raise forms.ValidationError("Фотография должна быть не больше 5 МБ.")

        content_type = getattr(avatar, "content_type", "")
        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        if content_type and content_type not in allowed_types:
            raise forms.ValidationError("Поддерживаются только PNG, JPEG и WebP.")
        return avatar
