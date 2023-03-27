from django.db import models
from django.core.validators import MinLengthValidator

# Create your models here.
class Institute(models.Model):
    name = models.CharField(max_length=255)
    affiliation = models.CharField(max_length=255)
    street = models.CharField(max_length=50)
    postcode = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    telephone = models.CharField(max_length=50)
    email = models.EmailField()
    date_registered = models.DateTimeField(auto_now_add=True)

class Staff(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # birthday is not added for privacy reasons; uniqueness is guaranteed by email
    # birthday = models.DateField()
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=50)
    ACTIVE_CHOICES = [(True, 'Active'), (False, 'Inactive')]
    active = models.BooleanField(choices=ACTIVE_CHOICES, default=False)
    date_registered = models.DateTimeField(auto_now_add=True)

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    date_registered = models.DateTimeField(auto_now_add=True)

class Method(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    method_folder = models.CharField(max_length=255, null=True)
    date_registered = models.DateTimeField(auto_now_add=True)

class FundingBody(models.Model):
    name = models.CharField(max_length=255)

class Project(models.Model):
    funding_body = models.ForeignKey(FundingBody, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=50)
    funding_number = models.CharField(max_length=50)
    funding_period_start = models.DateField()
    funding_period_end = models.DateField()
    project_folder = models.CharField(max_length=255, null=True)
    date_registered = models.DateTimeField(auto_now_add=True)

class SampleType(models.Model):
    name = models.CharField(max_length=255)

class Sample(models.Model):
    sample_id = models.CharField(max_length=20, validators=[MinLengthValidator(20)], primary_key=True)
    institute = models.ForeignKey(Institute, on_delete=models.PROTECT)
    method = models.ForeignKey(Method, on_delete=models.PROTECT, null=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    sample_type = models.ForeignKey(SampleType, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    parent_id = models.CharField(max_length=20, validators=[MinLengthValidator(20)])
    name = models.CharField(max_length=255)
    date_created = models.DateField()
    sample_info = models.CharField(max_length=255)
    supplementary_file = models.CharField(max_length=255)
    date_registered = models.DateTimeField(auto_now_add=True)
    
class Experiment(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.PROTECT)
    method = models.ForeignKey(Method, on_delete=models.PROTECT)
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    date_created = models.DateField()
    experiment_folder = models.CharField(max_length=255)
    date_registered = models.DateTimeField(auto_now_add=True)