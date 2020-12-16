from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# rest framework testing helpers
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('users:create_user')
TOKEN_URL = reverse('users:auth_token')
USER_URL = reverse('users:user')
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
            'name': 'Test Name'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """test that password is more than 5 characters"""
        payload = {
            'email': 'test@xontel.com',
            'password': 'test',
            'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """"test that token is created for a user"""
        payload = {
            'email': 'test@xontel.com',
            'password': 'test123456',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """test token is not created if invalid credentials"""
        create_user(email='test@xontel.com', password='test123456')
        payload = {
            'email': 'test@xontel.com',
            'password': 'wrong',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """test token is not created if user doesn't exist"""
        payload = {
            'email': 'test@xontel.com',
            'password': 'test123456',
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """test eamil and password are required"""
        res = self.client.post(TOKEN_URL, {
            'email': 'test',
            'password': ''
        })
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unautherized(self):
        """test authentication is required for user"""
        res = self.client.post(USER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """test api requests that requires authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@xontel.com',
            password='test123456',
            name='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """test retrieving profile for logged in user"""
        res = self.client.get(USER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_not_allowed(self):
        """test post not allowed on the update url"""
        res = self.client.post(USER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """test update authenticated user profile"""
        payload = {
            'name': 'New',
            'password': 'New123456',
        }
        res = self.client.patch(USER_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
