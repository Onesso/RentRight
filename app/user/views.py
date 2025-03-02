"""
Views for the user API
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    # it is added so that the view can be browsable
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# RetrieveUpdateAPIView is provided by drf provides
# functionality to retrive and update objects in the db
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    # we are using token to confirm that user are the user we know
    authentication_classes = [authentication.TokenAuthentication]
    # permission let us know the user and what he can do
    permission_classes = [permissions.IsAuthenticated]

    # we are overiding the get request and just retriving the user
    def get_object(self):
        """Retrive and return the authenticated user"""
        return self.request.user
