"""
Test for django admin modification
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """List of test for django admin"""

    def setUp(self):
        """test for creating user and clients"""
        # Creates a simulated web client to make requests.
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        # Logs in as the admin using force_login(self.admin_user)
        # to bypass authentication.
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name="Test User",
        )

    def test_users_list(self):
        """test that users are listed on page"""
        # Generates the URL for the user list page in (/admin/core/user/).
        url = reverse('admin:core_user_changelist')
        # Makes a request as the admin user to fetch the list of users.
        res = self.client.get(url)
        # Checks if the response contains the normal user's name
        # and email. it it contains the test will pass
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """test that edit page works"""
        # generate a page for the specific user id to be editted
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """tests create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
