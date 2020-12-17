from django.test import TestCase
from django.contrib.auth import get_user_model
from .. import models


def sample_user(email='test@xontel.com', password='test123456'):
    """create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """test creating a new user with an email is successful"""
        email = 'test@xontel.com'
        password = 'test123456'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalization(self):
        """test email for new user is normalized"""
        email = 'test@XONTEL.com'
        user = get_user_model().objects.create_user(email, 'test123456')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123456')

    def test_create_new_superuser(self):
        """test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@xontel.com',
            'test123456'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """test tag exists and its string representation is correct👌"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        # assert when tag is converted to string it equals the name
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """test ingredient exists and its string representation is correct👌"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Cucumber"
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """test recipe exists and its string representation is correct👌"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and Mudhroom Sauce',
            time_minute=5,
            price=5.00
        )
        self.assertEqual(str(recipe), recipe.title)
