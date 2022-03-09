from msilib.schema import Class
from multiprocessing import context
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView, TemplateView
from django.views.generic.edit import FormView
from django.template.response import TemplateResponse
from django.shortcuts import render
from django.conf import settings

from .forms import ApplicantUserForm, AccountHolderForm
import os

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


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
        if self.request.method == "GET":
            '''
            Add static files to template context
            '''
            context_dict = {}
            files = os.listdir(settings.STATIC_ROOT + "/images/home/")
            files = ["/images/home/"+ file for file in files]
            context_dict['files'] = files
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
            if form.add_user(user_email, password): 
                '''
                perform user login and provide redirected login page
                '''
                return render(request, "pages/home.html")
            else: return render(request, template_name=self.template_name, context={"form":form})
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
                    return render(request, "pages/home.html") 
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
