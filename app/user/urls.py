"""
URL Mapping for the user API
"""
from django.urls import path

from user import views  # from the app/user

# Defines the application namespace for the URLs.
# This is useful when multiple apps in a project have URLs with the same name.
app_name = 'user'

# A list of URL patterns for the user app.
# Each entry in the list maps a URL path to a view.
urlpatterns = [
    # Specifies the view that will handle requests to this URL.
    # Converts the class-based view(CreateUserView frow views.py)
    # into a callable function that Django can use to handle the request.
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token', views.CreateTokenView.as_view(), name='token')
]

"""
Summary

Maps the URL path create/ to the CreateUserView view.

Uses the user app namespace to avoid conflicts with URLs in other apps.

Allows the CreateUserView to handle requests for creating new users.
"""
