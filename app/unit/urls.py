"""
URL mapping for the unit api
Defaultrouter for dynamically generating urls
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from unit import views


router = DefaultRouter()
router.register('units', views.UnitViewSet)

app_name = 'unit'

urlpatterns = [
    path('', include(router.urls)),
]
