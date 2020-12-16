from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# rest framework testing helpers
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('users:create_user')
# helper function for pieces of code that is going to be used
# many times
# **params list of dynamic params


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class publicUserApiTests(TestCase):
    """test the user api"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """test that a user is created successfully"""
        payload = {
            'email': 'test@xontel.com',
            'password': 'test123456',
            'name': 'Test User'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """test creating user that is already exist"""
        payload = {
            'email': 'test@xontel.com',
            'password': 'test123456',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """test that password is more than 5 characters"""
        payload = {
            'email': 'test@xontel.com',
            'password': 'test',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
