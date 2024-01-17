import json
import os
import zipfile
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from main.models import Experiment, FundingBody, Method, Project, Sample, Staff
from main.serializers import (SampleTypeBatterySerializer, SampleTypeLiquidSerializer,
                              SampleTypeSolidsSerializer, SampleTypeSuspensionSerializer,
                              )


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

        # Print debug information on sample_info and sample_type
        # print("Sample info: ", sample_info)
        # print("Sample type: ", sample_type)

        # Validate the JSON file based on the chosen sample type
        try:
            sample_info_json = json.load(sample_info)

            # Print debug information
            # print("Sample Info JSON: ", sample_info_json)
            # print("Sample Type: ", sample_type)

            if not self.validate_json_structure(sample_info_json, sample_type):
                raise forms.ValidationError(
                    "Invalid JSON structure for the selected sample type.")
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON file.")

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


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            "first_name", "last_name", "email", "telephone", "institute", "active"]


User = get_user_model()


class UserForm(UserCreationForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(), required=False,
        widget=forms.SelectMultiple(attrs={"size": 3}))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2',
                  'email', 'institute', 'groups')

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
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
            user.save()
            user.institute.set(self.cleaned_data.get('institute'))
            groups = self.cleaned_data.get('groups')
            if groups:
                user.groups.set(groups)
        return user


class UserUpdateForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(), required=False,
        widget=forms.SelectMultiple(attrs={"size": 3}))

    class Meta:
        model = User
        fields = ('username', 'email', 'institute', 'groups')

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
