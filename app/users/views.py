from rest_framework import generics
from .serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """creates new user"""
    serializer_class = UserSerializer
