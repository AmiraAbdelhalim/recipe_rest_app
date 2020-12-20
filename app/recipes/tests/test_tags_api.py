from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# rest framework testing helpers
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe

from ..serializers import TagSerializer

TAGS_URL = reverse('recipes:tag-list')


class PublicTagsApiTests(TestCase):
    """test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test login required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """test authorized tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@xontel.com',
            'test123456',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        # many=True for the serializer to know its not a single object
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_retrieved_limited_to_user(self):
        """test tags retrieved are for logged in user"""
        user2 = get_user_model().objects.create_user(
            'user2@xontel.com',
            'testpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Oriental Food')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """test creating a new tag"""
        payload = {
            'name': 'test tag'
        }
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """test creating a new tag with invalid payload"""
        payload = {
            'name': ''
        }
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        """test filtering tags by assigned recipes"""
        tag1 = Tag.objects.create(user=self.user, name="Vegan")
        tag2 = Tag.objects.create(user=self.user, name="Fruity")

        recipe = Recipe.objects.create(
            title='CheeseCake',
            time_minute=20,
            price=20.00,
            user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(
            user=self.user,
            name="Breakfast"
        )
        Tag.objects.create(
            user=self.user,
            name="Lunch"
        )
        recipe1 = Recipe.objects.create(
            title='CheeseCake',
            time_minute=20,
            price=20.00,
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='PanCake',
            time_minute=10,
            price=10.00,
            user=self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
