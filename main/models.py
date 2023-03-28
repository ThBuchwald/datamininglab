from django.db import models
from django.core.validators import MinLengthValidator

# Create your models here.
class Institute(models.Model):
    name = models.CharField(max_length=255)
    affiliation = models.CharField(max_length=255, null=True, blank=True,
                  help_text="if applicable: umbrella organization")
    street = models.CharField(max_length=50)
    postcode = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    # could in the future be changed to PhoneNumberField
    telephone = models.CharField(max_length=50,
                help_text="e.g. administration office")
    email = models.EmailField(help_text="e.g. administration office")
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

class Staff(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.PROTECT,
                related_name="staff_members")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # birthday is not added for privacy reasons; uniqueness is guaranteed by email
    # birthday = models.DateField()
    email = models.EmailField(unique=True)
    # could in the future be changed to PhoneNumberField
    telephone = models.CharField(max_length=50)
    ACTIVE_CHOICES = [(True, 'Active'), (False, 'Inactive')]
    active = models.BooleanField(choices=ACTIVE_CHOICES, default=False,
             help_text="employment status")
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.first_name + " " + self.last_name

    class Meta:
        verbose_name_plural = "Staff"

class User(models.Model):
    # this information is set by Django or Django admin, no user input required
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

class Method(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.PROTECT,
                related_name="methods")
    name = models.CharField(max_length=255)
    # if additional information for the method is supplied, it will be stored in method_folder
    method_folder = models.CharField(max_length=255, null=True, blank=True)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

class FundingBody(models.Model):
    # lookup table for Project
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name

class Project(models.Model):
    funding_body = models.ForeignKey(FundingBody, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=50)
    funding_number = models.CharField(max_length=50)
    funding_period_start = models.DateField()
    funding_period_end = models.DateField()
    project_folder = models.CharField(max_length=255, null=True, blank=True)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

class SampleType(models.Model):
    # lookup table for Sample
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name

class Sample(models.Model):
    sample_id = models.CharField(max_length=20, validators=[MinLengthValidator(20)], primary_key=True,
                help_text="a unique 20-character identifier for the sample")
    institute = models.ForeignKey(Institute, on_delete=models.PROTECT, related_name="samples")
    method = models.ForeignKey(Method, on_delete=models.PROTECT, null=True, blank=True,
             related_name="samples")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="samples")
    sample_type = models.ForeignKey(SampleType, on_delete=models.PROTECT, related_name="samples")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="samples")
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True,
             related_name="children")
    name = models.CharField(max_length=255, help_text="free text field")
    date_created = models.DateField(help_text="date of creation, rarely: delivery")
    sample_info = models.CharField(max_length=255, help_text="link to sample type-specific information",
                                   verbose_name="sample information file",)
    # will probably have to change to FileField in the future for uploads
    supplementary_file = models.CharField(max_length=255, null=True, blank=True,
                         verbose_name="supplementary file path",
                         help_text="if applicable: datasheet, etc.")
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

class Experiment(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.PROTECT, related_name="experiments")
    method = models.ForeignKey(Method, on_delete=models.PROTECT, related_name="experiments")
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name="experiments")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="experiments")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="experiments")
    name = models.CharField(max_length=255, help_text="free text field")
    date_created = models.DateField(help_text="when was the data created")
    # all experimental data will have to be zipped, so single file
    # will probably have to change to FileField in the future for uploads
    experiment_file = models.CharField(max_length=255, default="",
                      verbose_name="experimental data file path")
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name