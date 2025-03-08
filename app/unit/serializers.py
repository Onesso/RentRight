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

    def _get_or_create_tags(self, tags, unit):
        """Handles getting and creating tags as needed"""
        auth_user = self.context['request'].user

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            unit.tags.add(tag_obj)

    def create(self, validated_data):
        """Creating a unit"""
        tags = validated_data.pop('tags', [])  # removing tags
        # now create a unit without tags
        unit = Unit.objects.create(**validated_data)
        self._get_or_create_tags(tags, unit)

        return unit

    def update(self, instance, validated_data):
        """updating a unit"""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class UnitDetailSerializer(UnitSerializer):
    """serializer for units details view"""
    class Meta(UnitSerializer.Meta):
        fields = UnitSerializer.Meta.fields + ['description']
