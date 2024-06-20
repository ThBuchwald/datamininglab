import json
import os
import zipfile
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms.widgets import TextInput, NumberInput, DateInput
from rest_framework import serializers
from main.models import Experiment, FundingBody, Method, Institute, Project, Sample, Staff
from main.serializers import (SampleTypeBatterySerializer, SampleTypeLiquidSerializer,
                              SampleTypeSolidsSerializer, SampleTypeSuspensionSerializer,
                              )
from main.utils.email_utils import send_initial_reset_email


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ["name", "method", "date_created", "sample",
                  "staff", "project", "experiment_file"]

    def clean_experiment_file(self):
        file = self.cleaned_data.get('experiment_file')
        # Debug information
        # print(file)
        if file:
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension != '.zip':
                raise ValidationError("Only zip files are allowed.")
        return file


class FundingBodyForm(forms.ModelForm):
    class Meta:
        model = FundingBody
        fields = ["name"]


class MethodForm(forms.ModelForm):
    class Meta:
        model = Method
        fields = ["institute", "name", "method_file"]

    def clean_method_file(self):
        file = self.cleaned_data.get('method_file')
        if file:
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension != '.zip' or not zipfile.is_zipfile(file):
                raise ValidationError("Only zip files are allowed.")
        return file


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "abbreviation", "funding_number", "funding_body",
                  "funding_period_start", "funding_period_end", "project_file"]

    def clean_project_file(self):
        file = self.cleaned_data.get('project_file')
        if file:
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension != '.zip' or not zipfile.is_zipfile(file):
                raise ValidationError("Only zip files are allowed.")
        return file


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ["sample_id", "name", "parent", "method", "date_created",
                  "institute", "project", "sample_type", "sample_info", "supplementary_file"]

    def clean_supplementary_file(self):
        file = self.cleaned_data.get('supplementary_file')
        if file:
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension != '.zip' or not zipfile.is_zipfile(file):
                raise ValidationError("Only zip files are allowed.")
        return file

    def clean_sample_info(self):
        sample_info = self.cleaned_data.get('sample_info')
        sample_type = self.cleaned_data.get('sample_type')

        if not sample_info:
            raise forms.ValidationError("This field is required.")

        try:
            sample_info_json = json.load(sample_info)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON file. Please upload a valid JSON file.")
        except Exception as e:
            raise forms.ValidationError(f"An error occurred while processing the file: {e}")

        if not self.validate_json_structure(sample_info_json, sample_type):
            raise forms.ValidationError("Invalid JSON structure for the selected sample type.")

        return sample_info


    def validate_json_structure(self, json_data, sample_type):
        # Map sample types to their serializers
        sample_type_serializers = {
            'Battery': SampleTypeBatterySerializer,
            'Solids': SampleTypeSolidsSerializer,
            'Liquid': SampleTypeLiquidSerializer,
            'Suspension': SampleTypeSuspensionSerializer,
        }

        # Get the serializer for the chosen sample type
        serializer_class = sample_type_serializers.get(sample_type.name)

        if not serializer_class:
            return False

        # Validate the JSON data using the serializer
        serializer = serializer_class(data=json_data)

        if not serializer.is_valid():
            print(serializer.errors)  # Log serializer errors to console
            return False

        return True


def serializer_field_to_form_field(serializer_field):
    """
    Return the Django form field that corresponds to the provided serializer field.
    """
    if isinstance(serializer_field, serializers.CharField):
        return forms.CharField(max_length=serializer_field.max_length,
                               required=serializer_field.required)
    elif isinstance(serializer_field, serializers.FloatField):
        return forms.FloatField(min_value=serializer_field.min_value,
                                  max_value=serializer_field.max_value,
                                  required=serializer_field.required)
    elif isinstance(serializer_field, serializers.DateField):
        return forms.DateField(required=serializer_field.required)
    else: # fall back to CharField
        return forms.CharField(required=serializer_field.required)
    

# this class is dynamically changing depending on the chosen sample type
class SampleInfoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Retrieve the serializer class passed to the form
        serializer_class = kwargs.pop('serializer_class', None)
        super(SampleInfoForm, self).__init__(*args, **kwargs)

        # If a serializer class was provided, create form fields based on the serializer fields
        if serializer_class:
            serializer = serializer_class()
            for field_name, serializer_field in serializer.get_fields().items():
                form_field = serializer_field_to_form_field(serializer_field)
                # Let's specify the widget directly in the form field definition
                if isinstance(serializer_field, serializers.CharField):
                    form_field.widget = TextInput(attrs={'class': 'form-group__input'})
                elif isinstance(serializer_field, serializers.IntegerField):
                    form_field.widget = NumberInput(attrs={'class': 'form-group__input'})
                elif isinstance(serializer_field, serializers.DateField):
                    form_field.widget = DateInput(attrs={'class': 'form-group__input', 'type': 'date'})
                # Add similar cases for other field types as needed.
                self.fields[field_name] = form_field


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            "first_name", "last_name", "email", "telephone", "institute", "active"]


User = get_user_model()


class UserForm(UserCreationForm):
    # password will be created by the new user
    password1 = forms.CharField(required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(required=False, widget=forms.PasswordInput)

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(), required=False,
        widget=forms.SelectMultiple(attrs={"size": 3}))

    class Meta:
        model = User
        fields = ('username', #'password1', 'password2',
                  'first_name', 'last_name', 'email', 'institute', 'groups')

    def __init__(self, *args, current_user=None, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        if current_user:
            self.fields['institute'].queryset = current_user.institute.all()
            self.fields['groups'].queryset = current_user.groups.exclude(
                name='AdminGroup')
        else:
            self.fields['institute'].queryset = Institute.objects.none()
            self.fields['groups'].queryset = Group.objects.none()
        self.fields["institute"].initial = []
        self.fields["groups"].initial = []

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            dummy_password = "temporarypassword12345"
            user.set_password(dummy_password)
            user.set_unusable_password()
            user.save()
            self.save_m2m()
            user.institute.set(self.cleaned_data.get('institute'))
            groups = self.cleaned_data.get('groups')
            if groups:
                user.groups.set(groups)
            # mail needs to be send after the previous code, otherwise user info will not be available (yet)
            send_initial_reset_email(self.request, user)
        return user


class UserUpdateForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(), required=False,
        widget=forms.SelectMultiple(attrs={"size": 3}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'institute', 'groups')

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if current_user:
            self.fields['institute'].queryset = current_user.institute.all()
            self.fields['groups'].queryset = current_user.groups.exclude(
                name='AdminGroup')
        else:
            self.fields['institute'].queryset = Institute.objects.none()
            self.fields['groups'].queryset = Group.objects.none()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.institute.set(self.cleaned_data.get('institute'))
            groups = self.cleaned_data.get('groups')
            if groups:
                user.groups.set(groups)
        return user
