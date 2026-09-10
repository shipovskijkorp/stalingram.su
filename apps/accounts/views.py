from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import IdentifierAuthenticationForm, RegisterForm


class StalingramLoginView(LoginView):
    authentication_form = IdentifierAuthenticationForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class StalingramLogoutView(LogoutView):
    next_page = "accounts:login"


def register(request):
    if request.user.is_authenticated:
        return redirect("messenger:home")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="apps.accounts.backends.EmailOrUsernameBackend")
        messages.success(request, "Учётная запись создана.")
        return redirect("messenger:home")

    return render(request, "accounts/register.html", {"form": form})
