from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import IdentifierAuthenticationForm, ProfileForm, RegisterForm
from .models import User


class StalingramLoginView(LoginView):
    authentication_form = IdentifierAuthenticationForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class StalingramLogoutView(LogoutView):
    next_page = "accounts:login"


class StalingramPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        messages.success(self.request, "Пароль изменён.")
        return super().form_valid(form)


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


@login_required
def profile(request):
    old_avatar_name = request.user.avatar.name if request.user.avatar else ""
    old_avatar_storage = request.user.avatar.storage if request.user.avatar else None

    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        if request.FILES.get("avatar") and old_avatar_name and old_avatar_storage:
            if old_avatar_name != user.avatar.name:
                old_avatar_storage.delete(old_avatar_name)
        messages.success(request, "Профиль сохранён.")
        return redirect("accounts:profile")

    return render(request, "accounts/profile.html", {"form": form})


@login_required
@require_POST
def remove_avatar(request):
    if request.user.avatar:
        request.user.avatar.delete(save=False)
        request.user.avatar = ""
        request.user.save(update_fields=["avatar"])
        messages.success(request, "Фотография профиля удалена.")
    return redirect("accounts:profile")


def public_profile(request, username):
    profile_user = get_object_or_404(User, username__iexact=username, is_active=True)
    return render(
        request,
        "accounts/public_profile.html",
        {"profile_user": profile_user},
    )
