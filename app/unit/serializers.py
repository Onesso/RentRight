"""
Serializer for Unit APIs
"""
from rest_framework import serializers

from core.models import (
    Unit,
    Tag,
    )


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only = ['id']


class UnitSerializer(serializers.ModelSerializer):
    """Serializer for Units"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Unit
        fields = ['id', 'title', 'price', 'link', 'tags']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Creating a unit"""
        tags = validated_data.pop('tags', [])  # removing tags
        # now create a unit without tags
        unit = Unit.objects.create(**validated_data)

        auth_user = self.context['request'].user

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            unit.tags.add(tag_obj)

        return unit


class UnitDetailSerializer(UnitSerializer):
    """serializer for units details view"""
    class Meta(UnitSerializer.Meta):
        fields = UnitSerializer.Meta.fields + ['description']
