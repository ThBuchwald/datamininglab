from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from main.models import User, Staff, Method, FundingBody, Project, SampleType, Sample, Experiment
from main.forms import UserForm, StaffForm


class CreateHome(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy("login")
    template_name = "main/create.html"


class SampleCreateView(CreateView):
    model = Sample
    fields = "__all__"
    success_url = reverse_lazy("home")


class ExperimentCreateView(CreateView):
    model = Experiment
    fields = "__all__"
    success_url = reverse_lazy("home")


class UserCreateView(CreateView):
    model = User
    form_class = UserForm
    success_url = reverse_lazy("home")

    # get_form is superseded to only send institutes belonging to the current user
    # https://stackoverflow.com/questions/48089590/limiting-choices-in-foreign-key-dropdown-in-django-using-generic-views-createv
    def get_form(self, *args, **kwargs):
        form = super(UserCreateView, self).get_form(*args, **kwargs)
        form.fields['institute'].queryset = self.request.user.institute.all()
        # the AdminGroup is exluded in this list to prevent admins from creating new admins
        form.fields['groups'].queryset = self.request.user.groups.all()[1:]
        return form


class StaffCreateView(CreateView):
    model = Staff
    form_class = StaffForm
    success_url = reverse_lazy("home")

    def get_form(self, *args, **kwargs):
        form = super(StaffCreateView, self).get_form(*args, **kwargs)
        form.fields['institute'].queryset = self.request.user.institute.all()
        # the AdminGroup is exluded in this list to prevent admins from creating new admins
        return form

# this is a little function to try ORM stuff


def say_hello(request):
    result = User.objects.get(id=2).institute.all()
    return HttpResponse(result)
