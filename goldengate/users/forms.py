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
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field

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

class UserDetailForm(forms.ModelForm):
    class Meta:
        model = ApplicantUser
        fields = ['first_name', 'last_name', 'user_email', 'phone_number', 'county', 'district', 'division']

    def __init__(self, *args, **kwargs):
        super(UserDetailForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'user_email',
            'phone_number',
            Row(
                Column('county', css_class='form-group col-md-6 mb-0'),
                Column('district', css_class='form-group col-md-4 mb-0'),
                Column('division', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
        )
        for nam, field in self.fields.items(): field.widget.attrs['readonly'] = True 

     
class ApplicantUserForm(forms.ModelForm):
    
    # password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = ApplicantUser
        fields = ['first_name', 'last_name', 'user_email', 'phone_number', 'county', 'district', 'division']

    def __init__(self, *args, **kwargs):
        super(ApplicantUserForm, self).__init__(*args, **kwargs)

        #TO-DO: Update password to use hashing
        self.fields['password'] = forms.CharField(widget=forms.PasswordInput())
 
    # Put in custom signup logic
    def add_user(self, request, email, password, **extra_fields):
        '''
        Check if user exists in the database, if not add them and email a welcome message.
        '''
        user = get_user_model()
        if not user.objects.exclude().filter(user_email=email).exists():
            user.objects.create_user(email, password, **extra_fields)
            '''
            authenticate user. Where to obtain request object from ?
            '''
            authenticated_user = authenticate(request, username=email, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                return True
        else:
            self.add_error(field="user_email", error=forms.ValidationError("Username already registered to an account."))
            return False

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
