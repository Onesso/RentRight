"""
Test for models
"""
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models  # other api we use models directly


# a helper function that creates a test user to assign to our tags
def create_user(email="test@example.com", password="testpass123"):
    """create and return a generic user"""
    return get_user_model().objects.create_user(email, password)


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

    def test_create_tag(self):
        """Test creating a tag is successfull"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_details(self):
        """Test creating a details is succeessfull"""
        user = create_user()
        details = models.Detail.objects.create(user=user, name='Details')

        self.assertEqual(str(details), details.name)

    @patch('core.models.uuid.uuid4')
    def test_unit_file_name_uuid(self, mock_uuid):
        """Test creating image path"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.unit_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/unit/{uuid}.jpg')
