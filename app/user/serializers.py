"""
Serializers for the user API view
"""

from django.contrib.auth import get_user_model #A Django utility to fetch the user model defined in the project core/models.py
from rest_framework import serializers # take a JSON input form the API, Validates the input and stores it in the model


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length':5}} #Allows additional configuration for specific fields.Prevents the password from being included in API responses.

    def create(self, validated_data): #Converts validated data into a new user instance in the database, ensuring the password is securely hashed.
        """Create and return a user with encrypted data"""
        return get_user_model().objects.create_user(**validated_data) #Uses create_user method (which is the custom user model i wrote on core/models.py) to create a new user with the provided data.