from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """serializer for user object """

    class Meta:
        model = get_user_model()
        # fields returned in json
        fields = ('email', 'password', 'name')
        # allow configurations of extra settings in model serializer
        # we use it to ensure the password is write only and min 5 chars
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5}
        }

    # validated_data json in the request
    def create(self, validated_data):
        """create a new user with encrypted password and return user"""
        return get_user_model().objects.create_user(**validated_data)
