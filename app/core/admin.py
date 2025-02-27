"""
Django admin customization.
This code customizes the Django admin interface for the User model.
It modifies how the User model is displayed and managed in the Django admin panel.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin #Imports the default UserAdmin class from Django's authentication admin module. This is used as a base class for customization.
from core import models
from django.utils.translation import gettext_lazy as _

class UserAdmin(BaseUserAdmin): #Inheritance: Inherits from BaseUserAdmin (Django's default UserAdmin class) to reuse its functionality while adding customizations.
    """Define admin pages for users"""
    ordering = ['id'] #Users will be ordered by their id field (ascending order by default).
    list_display = ['email', 'name'] #Specifies the fields to display in the list view of the admin interface.
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

admin.site.register(models.User, UserAdmin) #Registers the User model with the Django admin interface using the custom UserAdmin class.