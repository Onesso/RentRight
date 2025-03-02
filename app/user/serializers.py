"""
Serializers for the user API view
"""
# A Django utility to fetch the user model defined in the project core/models
from django.contrib.auth import (
    get_user_model,
    authenticate
    )
# take a JSON input form the API,
# Validates the input and stores it in the model
from rest_framework import serializers
from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        # Allows additional configuration for specific fields.
        # Prevents the password from being included in API responses.
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # Converts validated data into a new user instance in the database,
    # ensuring the password is securely hashed.
    def create(self, validated_data):
        """Create and return a user with encrypted data"""
        # Uses create_user method (which is the custom user model i wrote on
        # core/models.py) to create a new user with the provided data.
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """update and return user"""
        password = validated_data.pop("password", None)  # passwrd default none
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    # validate method for our auth token serializer

    def validate(self, attrs):
        """validate and authenticate the user"""
        email = attrs.get("email")
        password = attrs.get("password")
        # the authentication function comes built in django
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with the provided credentials.")
            raise serializers.ValidationError(msg, code="autherization")

        attrs["user"] = user
        return attrs
