from msilib.schema import Class
from multiprocessing import context
from sys import prefix
from turtle import st
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView, TemplateView
from django.views.generic.edit import FormView
from django.views.decorators.csrf import requires_csrf_token

from django.template.response import TemplateResponse
from django.shortcuts import render
from django.conf import settings

from utils.storages import StaticRootS3Boto3Storage
from .forms import ApplicantUserForm, AccountHolderForm
import os, boto3, environ

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def dispatch(self, request, id):
        '''
        Query database for user using user email.
        '''
        users = get_user_model()
        user = users.objects.get(id=id)
        # usersQueryset = users.objects.filter(user_email=user_email)
        # if usersQueryset.count() > 1:
            # user = usersQueryset
        
        return render(request, "users/user_detail.html", context={'object':user})


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        return self.request.user.get_absolute_url()  # type: ignore [union-attr]

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()

class GoldenGateHomeView(TemplateView):


    template_name = "pages/home.html"
    form_class = ApplicantUserForm
    success_url = None
    
    def form_valid(self, form):
        return super().form_valid(form) 
    
    def dispatch(self, request, *args, **kwargs):
        
            context_dict = retrieveHomepageArticlesUrl(request)
            return render(request, template_name=self.template_name, context=context_dict)

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        return reverse('home')

    def get_context_data(self, **kwargs):
        ret = super(ApplicantUserFormView, self).get_context_data(**kwargs)
        return ret

homeView = GoldenGateHomeView.as_view()


class ApplicantUserFormView(FormView):

    template_name = "account/signup.html"
    form_class = ApplicantUserForm
    success_url = None

    def form_valid(self, form):
        return super().form_valid(form) 
    
    def dispatch(self, request, *args, **kwargs):
        if self.request.method == "POST":
            form = self.get_context_data()["form"]
            if form.is_valid():
                user_email = form.cleaned_data["user_email"]
                password = form.cleaned_data["password"]
                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]
                phone_number = form.cleaned_data["phone_number"]
                county = form.cleaned_data["county"]
                district = form.cleaned_data["district"]
                division = form.cleaned_data["division"]
                extra_fields = {"first_name":first_name, "last_name":last_name, "county":county, "district":district, "division":division} #phone_number missing          
                if form.add_user(request, user_email, password, **extra_fields): 
                    '''
                    perform user login and provide redirected login page
                    authenticate user and serve home page
                    '''
                    if form.authenticate_user(request, user_email, password):
                        context_dict = retrieveHomepageArticlesUrl(request)
                        return render(request, "pages/home.html", context=context_dict)
            else:
                '''obtain error message from field and resend sign up page ?''' 
                return render(request, template_name=self.template_name, context={"form":form})
        else:
            # return super(ApplicantUserFormView, self).dispatch(request, *args, **kwargs)
            form = self.get_context_data()["form"]
            return render(request, template_name=self.template_name, context={"form":form})


    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        return reverse('home')

    def get_context_data(self, **kwargs):
        ret = super(ApplicantUserFormView, self).get_context_data(**kwargs)
        return ret



applicant_user = ApplicantUserFormView.as_view()

class LoginUserView(FormView):

    template_name = "account/login.html"
    form_class = AccountHolderForm
    success_url = None

    def form_valid(self, form):
        return super().form_valid(form) 
    
    def dispatch(self, request, *args, **kwargs):
        if self.request.method == "POST":
            form = self.get_context_data()["form"]
            if form.is_valid():
                '''
                perform user login and provide redirected login page
                '''
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]    
                if form.authenticate_user(request, username, password):
                    context_dict = retrieveHomepageArticlesUrl(request)
                    return render(request, "pages/home.html", context=context_dict) 
                else: return render(request, template_name=self.template_name, context={"form":form})
            else: return render(request, template_name=self.template_name, context={"form":form})
        else:
            # return super(ApplicantUserFormView, self).dispatch(request, *args, **kwargs)
            form = self.get_context_data()["form"]
            return render(request, template_name=self.template_name, context={"form":form})


    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        return reverse('home')

    def get_context_data(self, **kwargs):
        ret = super(LoginUserView, self).get_context_data(**kwargs)
        return ret



account_holding_user = LoginUserView.as_view()



#view util methods

def retrieveHomepageArticlesUrl(request, context_dict = None):
    '''
    Retrieve the path/url to the homepage articles
    '''
    if not context_dict: context_dict = dict()
    
    if not settings.SETTINGS_MODULE == "config.settings.production":
        if request.method == "GET":
            '''
            Add static files to template context
            '''
            homepage_files = os.listdir(settings.STATIC_ROOT + "\\images\\home\\")
            homepage_relative_path = [settings.STATIC_URL + "images/home/"+ file for file in homepage_files]
            context_dict['files'] = homepage_relative_path
            return context_dict
        elif request.method == "POST": # Not sure why the if statement was put there in the first place. I believe articles should be retrieved on both POST and GET
            '''
            Add static files to template context
            '''
            homepage_files = os.listdir(settings.STATIC_ROOT + "\\images\\home\\")
            homepage_relative_path = [settings.STATIC_URL + "images/home/"+ file for file in homepage_files]
            context_dict['files'] = homepage_relative_path
            return context_dict
    else:
        env = environ.Env() 
        awsSession = boto3.Session(aws_access_key_id=env("DJANGO_AWS_ACCESS_KEY_ID"), aws_secret_access_key=env("DJANGO_AWS_SECRET_ACCESS_KEY"))
        bucket = awsSession.resource('s3').Bucket('golden-gate-bomet')
        bucketFiles = bucket.objects.filter(Prefix="static/images/home") #need a thread to periodically keep track of this
        if bucketFiles:
            file_urls = [settings.AWS_S3_CUSTOM_DOMAIN + "/" +file.key for file in bucketFiles]
            context_dict['files'] = file_urls
        else: context_dict['files'] = []

    return context_dict