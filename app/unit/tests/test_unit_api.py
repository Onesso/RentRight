"""
tests for units apis
"""
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Unit,
    Tag,
    Detail,)

from unit.serializers import (UnitSerializer, UnitDetailSerializer)

UNITS_URL = reverse('unit:unit-list')


def detail_url(unit_id):
    """Create and return a unit detail url"""
    return reverse('unit:unit-detail', args=[unit_id])


def image_upload_url(unit_id):
    """Create and return an image upload url"""
    return reverse('unit:unit-upload-image', args=[unit_id])


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


def create_user(**params):
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='test@example.com',
                                password='testpassword123')
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
        other_user = create_user(
            email='otheruser@example.com', password='otheruserpassword123')
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

    # further robust testing
    def test_partial_update(self):
        """Test partial update of a unit"""
        original_link = 'https://example.com/unit.pdf'
        unit = create_unit(
            user=self.user,
            title='Sample unit title',
            link=original_link,
        )

        payload = {'title': 'New unit title'}
        url = detail_url(unit.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        unit.refresh_from_db()
        self.assertEqual(unit.title, payload['title'])
        self.assertEqual(unit.link, original_link)
        self.assertEqual(unit.user, self.user)

    def test_full_update(self):
        """Test full update of unit"""
        unit = create_unit(
            user=self.user,
            title='sample unit title',
            link='https://example.com/unit.pdf',
            price=Decimal('34000'),
            description='sample unit description',
        )

        payload = {
            'title': 'New unit title',
            'link': 'https://example.com/new-unit',
            'description': 'New unit description',
            'price': Decimal('35000'),
        }
        url = detail_url(unit.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        unit.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(unit, k), v)

        self.assertEqual(unit.user, self.user)

    # can not change the user associated with a unit
    def test_update_user_returns_error(self):
        """Test changing the unit user result to an error"""
        new_user = create_user(
            email='newuser@example.com',
            password='pass123@')
        unit = create_unit(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(unit.id)
        self.client.patch(url, payload)

        unit.refresh_from_db()
        self.assertEqual(unit.user, self.user)

    def test_delete_unit(self):
        """Test deleting a unit successful"""
        unit = create_unit(user=self.user)

        url = detail_url(unit.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Unit.objects.filter(id=unit.id).exists())

    def test_delete_other_user_unit(self):
        """Test trying to delete other user unit gives error"""
        new_user = create_user(
            email='newuser@example.com',
            password='pass123#')
        unit = create_unit(user=new_user)

        url = detail_url(unit.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Unit.objects.filter(id=unit.id).exists())

    def test_create_unit_with_new_tags(self):
        """Test creating a unit with tag."""
        payload = {
            'title': 'new unit title',
            'price': Decimal('4300.50'),
            'tags': [{'name': 'tag 1'}, {'name': 'tag2'}]
        }
        res = self.client.post(UNITS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        units = Unit.objects.filter(user=self.user)
        self.assertEqual(units.count(), 1)
        unit = units[0]
        self.assertEqual(unit.tags.count(), 2)
        for tag in payload['tags']:
            exists = unit.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_unit_with_existing_tag(self):
        """Test creating a unit with existing tags"""
        tag_tag2 = Tag.objects.create(user=self.user, name='tag2')
        payload = {
            'title': 'new unit title',
            'price': Decimal('4300.50'),
            'tags': [{'name': 'tag 1'}, {'name': 'tag2'}]
        }
        res = self.client.post(UNITS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        units = Unit.objects.filter(user=self.user)
        self.assertEqual(units.count(), 1)
        unit = units[0]
        self.assertEqual(unit.tags.count(), 2)
        self.assertIn(tag_tag2, unit.tags.all())
        for tag in payload['tags']:
            exists = unit.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    # when updating a unit u can also add a tag
    def test_create_tag_on_update(self):
        """Creating a tag when updating unit"""
        unit = create_unit(user=self.user)

        payload = {'tags': [{'name': 'tag1'}]}
        url = detail_url(unit.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='tag1')
        self.assertIn(new_tag, unit.tags.all())

    def test_update_unt_assign_tag(self):
        """Test assign an existing tag when updating a unit"""
        tag_one = Tag.objects.create(user=self.user, name='One')
        unit = create_unit(user=self.user)
        unit.tags.add(tag_one)

        tag_two = Tag.objects.create(user=self.user, name='Two')
        payload = {'tags': [{'name': 'Two'}]}
        url = detail_url(unit.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_two, unit.tags.all())
        self.assertNotIn(tag_one, unit.tags.all())

    def test_clear_unit_tags(self):
        """Test clear unit tags"""
        tag_one = Tag.objects.create(user=self.user, name='one')
        unit = create_unit(user=self.user)
        unit.tags.add(tag_one)

        payload = {'tags': []}
        url = detail_url(unit.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(unit.tags.count(), 0)

    def test_creating_unit_with_new_detail(self):
        """Test creating a unit with new detail"""
        payload = {
            'title': 'Title 1',
            'price': Decimal('2345.50'),
            'details': [{'name': 'details one'}, {'name': 'detail two'}]
        }
        res = self.client.post(UNITS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        units = Unit.objects.filter(user=self.user)
        self.assertEqual(units.count(), 1)
        unit = units[0]
        self.assertEqual(unit.details.count(), 2)
        for detail in payload['details']:
            exists = unit.details.filter(name=detail['name'],
                                         user=self.user).exists()
            self.assertTrue(exists)

    # creating units with some existing details
    # to acertain that it will not dublicate
    def test_create_unit_with_existing_details(self):
        """test creating unit with existing details"""
        detail = Detail.objects.create(user=self.user, name='detail 1')
        payload = {
            'title': 'title 1',
            'price': '34532.64',
            'details': [{'name': 'detail 1'}, {'name': 'name2'}]
        }
        res = self.client.post(UNITS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        units = Unit.objects.filter(user=self.user)
        self.assertEqual(units.count(), 1)
        unit = units[0]
        self.assertEqual(unit.details.count(), 2)  # if 3 dublicate true
        self.assertIn(detail, unit.details.all())
        for detail in payload['details']:  # looping details payload
            exists = unit.details.filter(name=detail['name'],
                                         user=self.user).exists()
            self.assertTrue(exists)

    def test_create_unit_on_update(self):
        """Creating a detail when updating the unit"""
        unit = create_unit(user=self.user)

        payload = {'details': [{'name': 'Limes'}]}
        url = detail_url(unit.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_detail = Detail.objects.get(user=self.user, name='Limes')
        self.assertIn(new_detail, unit.details.all())

    def test_update_unit_assign_detail(self):
        """Test assing an existing detail when updating a unit"""
        detail1 = Detail.objects.create(user=self.user, name='detail1')
        unit = create_unit(user=self.user)
        unit.details.add(detail1)

        detail2 = Detail.objects.create(user=self.user, name='detail2')
        payload = {'details': [{'name': 'detail2'}]}
        url = detail_url(unit.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(detail2, unit.details.all())
        self.assertNotIn(detail1, unit.details.all())

    def test_clear_unit_details(self):
        """test clearing unt details"""
        details = Detail.objects.create(user=self.user, name='detail')
        unit = create_unit(user=self.user)
        unit.details.add(details)

        payload = {'details': []}
        url = detail_url(unit.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(unit.details.count(), 0)


class ImageUploadTest(TestCase):
    """Test for image upload api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'test123pass',
        )
        self.client.force_authenticate(self.user)
        self.unit = create_unit(user=self.user)

    # to make sure image that test creates are deleted
    def tearDown(self):
        self.unit.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a unit"""
        url = image_upload_url(self.unit.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.unit.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.unit.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.unit.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
