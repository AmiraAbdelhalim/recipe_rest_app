from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# rest framework testing helpers
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient, Recipe

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

    def test_create_ingredient_successful(self):
        """test creating a new ingredient"""
        payload = {
            'name': 'test ingredient'
        }
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredent_invalid(self):
        """test creating a new ingredirnt with invalid payload"""
        payload = {
            'name': ''
        }
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """test filtering ingredients by assigned recipes"""
        ingredient1 = Ingredient.objects.create(user=self.user, name="Apple")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Sugar")

        recipe = Recipe.objects.create(
            title='CheeseCake',
            time_minute=20,
            price=20.00,
            user=self.user
        )
        recipe.tags.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """test filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Salt"
        )
        Ingredient.objects.create(
            user=self.user,
            name="Lunch"
        )
        recipe1 = Recipe.objects.create(
            title='CheeseCake',
            time_minute=20,
            price=20.00,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='PanCake',
            time_minute=10,
            price=10.00,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
