"""
Формы приложения пользователей.
"""
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from .models import User


class UserRegisterForm(UserCreationForm):
    """Форма регистрации с подтверждением email."""

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone", "password1", "password2")


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "avatar")


class UserPasswordResetForm(PasswordResetForm):
    """Форма восстановления пароля."""

    email = forms.EmailField(label="Email", max_length=254)


class UserSetPasswordForm(SetPasswordForm):
    """Форма установки нового пароля."""
    pass
