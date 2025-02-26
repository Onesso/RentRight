"""
Database models
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, #contains functionality for the authentification system but not the fields
    PermissionsMixin, #contains functionality for the permission and fields that are needed for the permission feature
    BaseUserManager, #handles creation of user and superusers
)

"""create user model manager"""
class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return the new user"""
        if not email:
            raise ValueError("user must have a valid email address")
        user = self.model(email=self.normalize_email(email), **extra_fields) #creates a new user
        user.set_password(password) #hashes the password for security
        user.save(using=self._db) #save the user to the database

        return user



class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email' #specify that the email field is used for authentication