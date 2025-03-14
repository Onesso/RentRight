"""
Test for details api
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Detail

from unit.serializers import DetailSerializer

DETAILS_URL = reverse('unit:detail-list')


def detail_url(detail_id):
    """create and return details detail_url"""""
    return reverse('unit:detail-detail', args=[detail_id])


def create_user(email='test@example.com', password='test123'):
    """Create and return a user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicDetailsAPITests(TestCase):
    """Test unauthenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving details"""
        res = self.client.get(DETAILS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDetailsAPITestCase(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_details(self):
        """Test retrieving a list of details"""
        Detail.objects.create(user=self.user, name='detail 1')
        Detail.objects.create(user=self.user, name='detail 1')

        res = self.client.get(DETAILS_URL)

        details = Detail.objects.all().order_by('-name')
        serializer = DetailSerializer(details, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_details_limited_to_user(self):
        """test list details limited to the authenticated user"""
        user2 = create_user(email='user2@exmple.com')
        Detail.objects.create(user=user2, name='deteil_user2')
        details = Detail.objects.create(user=self.user, name='detail1')

        res = self.client.get(DETAILS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], details.name)
        self.assertEqual(res.data[0]['id'], details.id)

    def test_update_detail(self):
        """Test for updating a detail"""
        detail = Detail.objects.create(user=self.user, name='detail1')

        payload = {'name': 'detail2'}
        url = detail_url(detail.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        detail.refresh_from_db()
        self.assertEqual(detail.name, payload['name'])

    def test_delete_detail(self):
        """Test for deleting details"""
        detail = Detail.objects.create(user=self.user, name='details')
        url = detail_url(detail.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        details = Detail.objects.filter(user=self.user)
        self.assertFalse(details.exists())
