from __future__ import division
from typing_extensions import Self
from xml.dom import ValidationErr
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django import forms
from allauth.account.forms import SignupForm

User = get_user_model()


class UserChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(admin_forms.UserCreationForm):
    
    class Meta(admin_forms.UserCreationForm.Meta):
        model = User

        error_messages = {
            "username": {"unique": _("This username has already been taken.")}
        }

class ApplicantUserForm(forms.Form):
    '''User leaving information to be contacted by goldengate'''


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
    def add_user(self, username, password):
        '''
        Check if user exists in the database, if not add them and email a welcome message.
        '''
        user = get_user_model()
        if not user.objects.exclude().filter(username=username).exists():
            user.objects.create_user(username=username, password=password)
        else:
            self.add_error(field="user_email", error=forms.ValidationError("Username already registered to an account."))
