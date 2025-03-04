"""
Views for unit api
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Unit
from unit import serializers


class UnitViewSet(viewsets.ModelViewSet):
    """View for managing Unit APIs"""
    serializer_class = serializers.UnitSerializer
    queryset = Unit.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retriving Units for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')
