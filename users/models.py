"""
Модели приложения пользователей.
"""
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя (email вместо username)."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен для регистрации.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Email используется как основное поле для входа.
    """

    username = models.CharField(max_length=150, null=True, blank=True, unique=False)
    email = models.EmailField("Email", unique=True)
    first_name = models.CharField("Имя", max_length=50, blank=True)
    last_name = models.CharField("Фамилия", max_length=50, blank=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    avatar = models.ImageField("Аватар", upload_to="users/", blank=True, null=True)
    is_active = models.BooleanField("Активен", default=False)
    email_verify_token = models.UUIDField(
        "Токен подтверждения email", default=uuid.uuid4, editable=False
    )
    is_manager = models.BooleanField("Менеджер", default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
