"""
Forms for authentication.
"""
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)
from django.contrib.auth import get_user_model


class CustomUserCreationForm(UserCreationForm):
    """Form for user registration."""

    username = forms.CharField(
        label='Username',
        required=True
    )
    email = forms.EmailField(
        required=True
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        strip=False,
        required=True
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput,
        strip=False,
        required=True
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')


class CustomAuthenticationForm(AuthenticationForm):
    """Authentication form for user login."""
    username = forms.CharField(
        label='Username'
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
    )
