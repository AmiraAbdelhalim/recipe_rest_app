from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


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
    # url api/users/create
    def create(self, validated_data):
        """create a new user with encrypted password and return user"""
        return get_user_model().objects.create_user(**validated_data)

    # url api/users/user (with access token)
    # put (update the entire entity)
    # patch (partial update)
    def update(self, instance, validated_data):
        """update user and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """serializer for the user authentication object"""

    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    # url api/users/token
    def validate(self, attrs):
        """"validate and authenticate user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('unable to authenticate with the provided credentials!!')
            raise serializers.ValidationError(msg, code='authentication')
        attrs['user'] = user
        return attrs
