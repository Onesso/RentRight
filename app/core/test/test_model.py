"""
Test for models
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models  # other api we use models directly


class Modeltests(TestCase):
    """Test model"""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """test if email is normalized for new user"""
        sample_emails = [
            # the local part retain the uppercase because self.normalize_email
            # from method BaseUserManager only converts the domain
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """"test that create a user without email raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test of creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_unit(self):
        """Test for creating property"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpassword123'
        )
        unit = models.Unit.objects.create(
            user=user,  # user that the unit belongs to
            title="Sample Title",
            # time_minutes=5,
            price=Decimal('5.50'),
            description='sample description',
        )
        self.assertEqual(str(unit), unit.title)
