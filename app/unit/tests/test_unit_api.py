"""
tests for units apis
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Unit

from unit.serializers import (UnitSerializer, UnitDetailSerializer)

UNITS_URL = reverse('unit:unit-list')


def detail_url(unit_id):
    """Create and return a unit detail url"""
    return reverse('unit:unit-detail', args=[unit_id])


# function returns default values to avoid repetition
def create_unit(user, **params):
    defaults = {
        'title': 'sample unit title',
        'description': 'Sample description',
        'price': Decimal('24000'),
        'link': 'http://example.com/unit.pdf',
    }
    defaults.update(params)

    unit = Unit.objects.create(user=user, **defaults)

    return unit


class PublicUnitAPITests(TestCase):
    """Test unauthenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call api"""
        res = self.client.get(UNITS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUnitAPITests(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'password123',
        )
        self.client.force_authenticate(self.user)

    # user in logged in and get a list of all units
    def test_retrieve_unit(self):
        """Test retriving a list of units"""
        create_unit(user=self.user)
        create_unit(user=self.user)

        res = self.client.get(UNITS_URL)

        units = Unit.objects.all().order_by('-id')
        serializer = UnitSerializer(units, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # user is logged in but gets a list of all his units
    def test_units_list_limited_to_user(self):
        """Test list of all units that are his/hers"""
        other_user = get_user_model().objects.create_user(
            'otheruser@example.com',
            'otheruserpassword123',
        )
        create_unit(user=other_user)
        create_unit(user=self.user)

        res = self.client.get(UNITS_URL)

        units = Unit.objects.filter(user=self.user)
        serializer = UnitSerializer(units, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_unit_details(self):
        """Test get unit details"""
        unit = create_unit(user=self.user)

        url = detail_url(unit.id)
        res = self.client.get(url)

        serializer = UnitDetailSerializer(unit)
        self.assertEqual(res.data, serializer.data)

    def test_create_unit(self):
        """Test creating a unit"""
        payload = {
            'title': 'sample unit',
            'price': Decimal('54000.00'),
        }
        res = self.client.post(UNITS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        unit = Unit.objects.get(id=res.data['id'])
        # k stands for key and v for value
        for k, v in payload.items():
            self.assertEqual(getattr(unit, k), v)
        self.assertEqual(unit.user, self.user)
