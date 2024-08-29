"""
Urls for authentication views.
"""

from django.urls import path

from authentication.views import (
    CustomLoginView,
    CustomLogOutView,
    RegisterView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogOutView.as_view(), name='logout'),
]
