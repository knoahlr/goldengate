from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import CharField, EmailField
from django.forms import BooleanField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper

from .managers import ApplicantUserManager

class ApplicantUser(AbstractBaseUser, PermissionsMixin):
    """
    Default user for GoldenGate.
    """

    #: First and last name do not cover name patterns around the globe
    # name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = CharField(max_length=100)  # type: ignore
    last_name = CharField(max_length=100)  # type: ignore
    user_email = EmailField(max_length=100, unique=True)
    
    # phone_number = RegexField(regex=r'^\+?1?\d{9,15}$', 
    #                             error_messages = {"required": "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."})

    county = CharField(max_length=100)
    district = CharField(max_length=100)
    division = CharField(max_length=100)

    #Attributes needed for it to work with admin
    is_staff = BooleanField(required=True) #Returns True if the user is allowed to have access to the admin site.
    is_active = BooleanField(required=True) #Returns True if the user account is currently active.

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = ApplicantUserManager()

    def __str__(self):
        return self.user_email

    def get_absolute_url(self):
        """Get url for user's detail view.
        Returns:
            str: URL for user detail.
        """
        return reverse("users:detail", kwargs={"username": self.username})

    #method needed for it to work with admin
    def has_perm(self, perm, obj=None):
        #Returns True if the user has the named permission. If obj is provided, the permission needs to be checked against a specific object instance.
        return True

    #method needed for it to work with admin
    def has_module_perms(self, app_label):
        #Returns True if the user has permission to access models in the given app.
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_staff

    @property
    def is_admin(self):
        "Is the user admin?"
        return self.is_admin