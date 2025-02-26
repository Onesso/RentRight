# """
# Database models
# """
# from django.db import models
# from django.contrib.auth.models import (
#     AbstractBaseUser, #contains functionality for the authentification system but not the fields
#     PermissionsMixin, #contains functionality for the permission and fields that are needed for the permission feature
#     BaseUserManager,
# )

# """create user model manager"""
# class Usermanager(BaseUserManager):
#     """Manager for users."""




# class User(AbstractBaseUser, PermissionsMixin):
#     """User in the system"""
#     email = models.EmailField(max_length=255, unique=True)
#     name = models.CharField(max_length=255)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     USERNAME_FIELD = 'email'