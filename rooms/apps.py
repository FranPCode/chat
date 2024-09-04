"""
Initial app configuration.
"""
from django.apps import AppConfig


class RoomsConfig(AppConfig):
    """
    Configuration class for the roomsapp.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rooms'
