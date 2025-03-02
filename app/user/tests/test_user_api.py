"""
Test for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model  # fetch the user model
from django.urls import reverse
# reverse Used to generate URLs for Django views by their name

from rest_framework.test import APIClient  # APIClient simulate HTTP requests
from rest_framework import status  # Provides HTTP status codes

CREATE_USER_URL = reverse('user:create')
# Generates the URL for the create endpoint in the user app's URL configuration
# This is the endpoint where new users are created.
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    # A helper function to create a user in the database
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)
    # the create_user in this line is
    #  inbuilt it is not the one defined above


class PublicUserApiTest(TestCase):
    """Test the public features for the user API"""

    def setUp(self):
        # setUp: A method that runs before each test. Here, it initializes an
        # APIClient instance to make HTTP requests during the tests.
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful via API"""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test user",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        # Fetches the newly created user from the database
        # using the email provided in the payload.
        self.assertTrue(user.check_password(payload["password"]))
        # Verifies that the password in the payload
        #  matches the user's password in the database.
        self.assertNotIn('password', res.data)
        # Ensures that the response data does not
        # include the user's password (for security reasons).

    def test_user_with_email_exist_error(self):
        """Test error returned if user with email already exist"""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test user",
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 5chars"""
        payload = {
            "email": "test@example.com",
            "password": "pw",
            "name": "Test name",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exist)

    # the function below test creating of a user
    # then creating of a payload
    def test_create_token_for_user(self):
        """test to generate token for valid user"""
        user_details = {
            "name": "Test user",
            "email": "test@example.com",
            "password": "test-user-password123",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"]
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # Test if provided with wrong credentials
    def test_create_token_bad_credentials(self):
        """Test returns error if bad credentials"""
        create_user(email='test@example.com', password='goodpass')
        payload = {"email": "test@example.com", "password": "badpass"}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test return error if no password"""
        payload = {"email": "test@example.com", "password": ""}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is requered for user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Test API request that require authentication"""

    # mock creating a user and forcing the user to authenticate
    # the assumption is user are authenticated
    def setUp(self):
        self.user = create_user(
            email="test@example.com",
            password="testpass123",
            name="test name"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # since user is authenticated, make a get request for user details
    def test_retrive_profile_success(self):
        """test retriving profile for looged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    # the ME endpoint is not creating anything so we disable POST
    def test_post_me_not_allowed(self):
        """test the POST method is not allowed in ME endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # the ME endpoint will support the update of profile
    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'updated name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()  # to update the db on the new user info
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
