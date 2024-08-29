"""
User representation in admin site.
"""
from django.contrib import admin
from django.contrib.auth import get_user_model


class UserAdmin(admin.ModelAdmin):
    """User model in admin."""
    list_display = ('id', 'username', 'email')


admin.site.register(
    get_user_model(),
    UserAdmin
)
