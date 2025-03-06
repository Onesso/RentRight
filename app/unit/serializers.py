"""
Serializer for Unit APIs
"""
from rest_framework import serializers

from core.models import (
    Unit,
    Tag,
    )


class UnitSerializer(serializers.ModelSerializer):
    """Serializer for Units"""

    class Meta:
        model = Unit
        fields = ['id', 'title', 'price', 'link']
        read_only = ['id']


class UnitDetailSerializer(UnitSerializer):
    """serializer for units details view"""
    class Meta(UnitSerializer.Meta):
        fields = UnitSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only = ['id']
