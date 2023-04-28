from django import forms
from main.models import User, Staff


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username", "password", "first_name", "last_name", "email", "institute", "groups"]
        widgets = {
            "password": forms.PasswordInput,
            "institute": forms.Select,
            "groups": forms.SelectMultiple,
            "email": forms.EmailInput,
        }


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            "first_name", "last_name", "email", "telephone", "institute", "active"]
        widgets = {
            "institute": forms.Select,
            "email": forms.EmailInput,
        }
