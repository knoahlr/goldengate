from __future__ import division
import re
from typing_extensions import Self
from xml.dom import ValidationErr
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.utils.translation import gettext_lazy as _
from django import forms
from allauth.account.forms import SignupForm


# User = get_user_model()
from .models import ApplicantUser


class UserChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = ApplicantUser
        fields = {"first_name", "last_name", "user_email", "county", "district", "division"}

class UserCreationForm(admin_forms.UserCreationForm):
    
    class Meta(admin_forms.UserCreationForm.Meta):
        model = ApplicantUser
        fields = {"first_name", "last_name", "user_email", "county", "district", "division"}

        error_messages = {
            "user_email": {"unique": _("This email is already registered to a user.")}
        }

class ApplicantUserForm(forms.Form):
    '''
    User leaving information to be contacted by goldengate
    '''

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
    user_email = forms.EmailField(max_length=100)
    phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$', 
                                error_messages = {"required": "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."})
    county = forms.CharField(max_length=100)
    district = forms.CharField(max_length=100)
    division = forms.CharField(max_length=100)

    # Put in custom signup logic
    def add_user(self, email, password, **extra_fields):
        '''
        Check if user exists in the database, if not add them and email a welcome message.
        '''
        user = get_user_model()
        if not user.objects.exclude().filter(user_email=email).exists():
            user.objects.create_user(email, password, **extra_fields)
            return True
        else:
            self.add_error(field="user_email", error=forms.ValidationError("Username already registered to an account."))
            return False


class AccountHolderForm(forms.Form):
    '''User leaving information to be contacted by goldengate'''

    username = forms.EmailField(max_length=100)
    phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$', 
                                error_messages = {"required": "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."},
                                required=False)
    password = forms.CharField(widget=forms.PasswordInput())

    # Put in custom signup logic
    def authenticate_user(self, request, username, password):
        '''
        Check if user exists in the database, if not add them and email a welcome message.
        '''
        user = get_user_model()
        if user.objects.exclude().filter(user_email=username).exists():
            authenticated_user = authenticate(request, username=username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                return True
            else:
                self.add_error(field="username", error=forms.ValidationError("Wrong password supplied for user account"))
        else:
            self.add_error(field="username", error=forms.ValidationError("There's no account registered with that username."))
            return False