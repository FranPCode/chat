"""
Tests for authentication and creation forms.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from authentication.forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm
)

User = get_user_model()


class CustomUserCreationFormTests(TestCase):
    def test_form_valid_with_correct_data(self):
        """Test the correct form behavior """
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'testuser')

    def test_form_invalid_when_passwords_do_not_match(self):
        """Test when the two password no match."""
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword123',
            'password2': 'wrongpassword'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_invalid_when_missing_required_fields(self):
        """Test the correct behavior of the required fields."""
        form_data = {
            'username': '',
            'email': 'testuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_form_invalid_when_username_already_exists(self):
        """Test the correct behavior when a username already exists."""
        User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        form_data = {
            'username': 'testuser',
            'email': 'testuser2@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class CustomAuthenticationFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )

    def test_form_valid_with_correct_data(self):
        """Test the correct behavior of the authentication form."""
        form_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_incorrect_password(self):
        """test when the password no match with the username."""
        form_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors['__all__'][0])

    def test_form_invalid_with_nonexistent_username(self):
        """Test when the user dont exists."""
        form_data = {
            'username': 'nonexistentuser',
            'password': 'testpassword123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors['__all__'][0])

    def test_form_invalid_when_missing_required_fields(self):
        """Test the correct behavior when required fields are empty."""
        form_data = {
            'username': '',
            'password': 'testpassword123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
