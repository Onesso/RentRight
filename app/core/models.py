"""
Database models
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    # contains functionality for the authentification system but not the fields
    AbstractBaseUser,
    # contains functionality for the permission and
    # fields that are needed for the permission feature
    PermissionsMixin,
    BaseUserManager,  # handles creation of user and superusers
)

"""create user model manager"""


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return the new user"""
        if not email:
            raise ValueError("user must have a valid email address")
        # creates a new user
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)  # hashes the password for security
        user.save(using=self._db)  # save the user to the database

        return user

    def create_superuser(self, email, password):
        """"this method creates and returns asuperuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    # specify that the email field is used for authentication
    USERNAME_FIELD = 'email'


class Unit(models.Model):
    """Unit object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    details = models.ManyToManyField('Detail')

    def __str__(self):
        return self.title
        # This allows us to display the title in django admin instead of id


class Tag(models.Model):
    """Tag for filtering units"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
    # This return the string representation we were testing


class Detail(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
