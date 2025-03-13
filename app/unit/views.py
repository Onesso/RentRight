"""
Views for unit api
"""
from rest_framework import (
    viewsets,
    mixins,  # gives support to add additional functionalites
    status,
    )

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# modify to get all units
from rest_framework.decorators import action
from rest_framework.response import Response
# end
# actions add addition functionalities on top of the defaulst viewset func

from core.models import (
    Unit,
    Tag,
    Detail,
    )
from unit import serializers


class UnitViewSet(viewsets.ModelViewSet):
    """View for managing Unit APIs"""
    serializer_class = serializers.UnitDetailSerializer
    queryset = Unit.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retriving Units for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.UnitSerializer
        elif self.action == 'upload_image':
            return serializers.UnitImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new unit and is attached to the user who created it"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to unit."""
        unit = self.get_object()
        serializer = self.get_serializer(unit, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # start modify
    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def all_units(self, request):
        """Retrieve all units without filtering by user"""
        units = self.queryset.order_by('-id')
        serializer = self.get_serializer(units, many=True)
        return Response(serializer.data)
    # end


class BaseUnitAttrViewSet(mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """Base view set for unit attribute"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # this method overrides the default queryset to filter
    def get_queryset(self):
        """Filter queryset to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseUnitAttrViewSet):
    """Manage tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class DetailViewSet(BaseUnitAttrViewSet):
    """Manage details in the database"""
    serializer_class = serializers.DetailSerializer
    queryset = Detail.objects.all()
