from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# rest framework testing helpers
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from ..serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipes:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """test the publicly available ingredients api"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test login is required to access ingredients"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """test authorized ingredients api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@xontel.com',
            'test123456'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients_list(self):
        """test retrieving list of ingredients"""
        Ingredient.objects.create(
            user=self.user,
            name='Lemon'
        )
        Ingredient.objects.create(
            user=self.user,
            name='Salt'
        )
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """test ingredients retrieved are for logged in user"""
        user2 = get_user_model().objects.create_user(
            'user2@xontel.com',
            'testpass'
        )
        Ingredient.objects.create(user=user2, name='Pepper')
        ingredient = Ingredient.objects.create(user=self.user, name='Rice')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
