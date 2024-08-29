"""
Models for user.
"""
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
)


@deconstructible
class UnicodeUsernameValidator(validators.RegexValidator):
    """Validate if username not contains regular expressions."""
    regex = r"^[\w.@+-]+\Z"
    flags = 0


class CustomUserManager(BaseUserManager):
    """Custom manager for user model."""

    def create_user(self, username, password, **extra_fields):
        """Create and return an new user."""
        if not username or username == '':
            raise ValueError("The given username must be set")

        if not password or len(password) <= 8:
            raise ValueError(
                "The given password must be set and have 8 or more characters.")

        email = extra_fields.pop('email', '')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create(self, username, password, **extra_fields):
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser):
    """User Model."""

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[username_validator, ]
    )
    email = models.EmailField(
        blank=True,
    )
    is_staff = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=True,
    )
    date_joined = models.DateTimeField(
        auto_now=True,
    )

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
