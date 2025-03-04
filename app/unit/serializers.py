"""
Serializer for Unit APIs
"""
from rest_framework import serializers

from core.models import Unit


class UnitSerializer(serializers.ModelSerializer):
    """Serializer for Units"""

    class Meta:
        model = Unit
        fields = ['id', 'title', 'description', 'price', 'link']
        read_only = ['id']
