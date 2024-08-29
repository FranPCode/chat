"""
Views for authentication.
"""

from django.urls import reverse_lazy
from django.views.generic import (
    CreateView
)
from django.contrib.auth.views import (
    LoginView,
    LogoutView
)

from authentication.forms import (
    CustomAuthenticationForm,
    CustomUserCreationForm
)


class RegisterView(CreateView):
    """View for user registration."""
    form_class = CustomUserCreationForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CustomLoginView(LoginView):
    """Login view for users."""
    form_class = CustomAuthenticationForm
    template_name = 'authentication/login.html'
    next_page = reverse_lazy('index')


class CustomLogOutView(LogoutView):
    """Log out url for users.."""
    next_page = reverse_lazy('index')
