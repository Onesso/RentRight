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
        self.client = Client() #Creates a simulated web client to make requests.
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.admin_user) #Logs in as the admin using force_login(self.admin_user) to bypass authentication.
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name="Test User",
        )

    def test_users_list(self):
        """test that users are listed on page"""
        url = reverse('admin:core_user_changelist') #Generates the URL for the user list page in Django admin (/admin/core/user/).
        res = self.client.get(url) #Makes a request as the admin user to fetch the list of users.

        self.assertContains(res, self.user.name) #Checks if the response contains the normal user's name and email. it it contains the test will pass
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """test that edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id]) #generate a page for the specific user id to be editted
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """tests create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)