from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import default_storage
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os


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


class User(AbstractUser):
    institute = models.ManyToManyField(Institute)
    email = models.EmailField(unique=True)


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


class Method(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.PROTECT,
                                  related_name="methods")
    name = models.CharField(max_length=255)
    # if additional information for the method is supplied, it will be stored in method_folder
    method_file = models.FileField(upload_to="method_files",
                                   verbose_name="path to method files")
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    def get_method_file_upload_path(self, filename):
        # Use the instance's primary key as the new file name
        new_filename = f"{self.pk}.zip"
        return os.path.join('method_files', new_filename)

    def save(self, *args, **kwargs):
        # Save the instance to generate the primary key (if it's a new instance)
        is_new = self._state.adding
        super().save(*args, **kwargs)

        # Save the file into the new path and name created with the primary key
        if is_new and self.method_file:
            old_file_path = self.method_file.path
            new_file_name = self.get_method_file_upload_path(
                self.method_file.name)
            new_file_path = default_storage.path(new_file_name)
            os.rename(old_file_path, new_file_path)
            self.method_file.name = new_file_name
            super().save(update_fields=['method_file'])


@receiver(post_delete, sender=Method)
def delete_method_file(sender, instance, **kwargs):
    # Check if the method_file field is not empty
    if instance.method_file:
        # If the file exists in the storage, delete it
        if default_storage.exists(instance.method_file.name):
            default_storage.delete(instance.method_file.name)


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
    # if additional information for the project is supplied, it will be stored in project_folder
    project_file = models.FileField(upload_to="project_files",
                                    verbose_name="path to project files", null=True, blank=True)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    def get_project_file_upload_path(self, filename):
        # Use the instance's primary key as the new file name
        new_filename = f"{self.pk}.zip"
        return os.path.join('project_files', new_filename)

    def save(self, *args, **kwargs):
        # Save the instance to generate the primary key (if it's a new instance)
        is_new = self._state.adding
        super().save(*args, **kwargs)

        # Save the file into the new path and name created with the primary key
        if is_new and self.project_file:
            old_file_path = self.project_file.path
            new_file_name = self.get_project_file_upload_path(
                self.project_file.name)
            new_file_path = default_storage.path(new_file_name)
            os.rename(old_file_path, new_file_path)
            self.project_file.name = new_file_name
            super().save(update_fields=['project_file'])


@receiver(post_delete, sender=Project)
def delete_project_file(sender, instance, **kwargs):
    if instance.project_file:
        if default_storage.exists(instance.project_file.name):
            default_storage.delete(instance.project_file.name)


class SampleType(models.Model):
    # lookup table for Sample
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Sample(models.Model):
    sample_id = models.CharField(max_length=20, validators=[MinLengthValidator(20)], primary_key=True,
                                 help_text="a unique 20-character identifier for the sample")
    institute = models.ForeignKey(
        Institute, on_delete=models.PROTECT, related_name="samples")
    method = models.ForeignKey(Method, on_delete=models.PROTECT, null=True, blank=True,
                               related_name="samples")
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="samples")
    sample_type = models.ForeignKey(
        SampleType, on_delete=models.PROTECT, related_name="samples")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.DO_NOTHING)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True,
                               related_name="children")
    name = models.CharField(max_length=255, help_text="free text field")
    date_created = models.DateField(
        help_text="date of creation, rarely: delivery")
    # both sample_info and supplementary_files are renamed to the sample_id
    sample_info = models.FileField(upload_to='sample_info',
                                   help_text="link to sample type-specific information",
                                   verbose_name="sample information file",)
    supplementary_file = models.FileField(upload_to='supplementary_files', null=True, blank=True,
                                          verbose_name="supplementary file path",
                                          help_text="if applicable: datasheet, etc.")
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.sample_id

    def get_sample_info_upload_path(self):
        new_filename = f"{self.sample_id}.json"
        return os.path.join('sample_info', new_filename)

    def get_supplementary_file_upload_path(self, filename):
        if filename:
            ext = filename.split(".")[-1]
            new_filename = f"{self.sample_id}.{ext}"
            return os.path.join('supplementary_files', new_filename)
        return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Rename and save the sample_info file if the file name has changed
        new_sample_info_name = self.get_sample_info_upload_path()
        if self.sample_info and self.sample_info.name != new_sample_info_name:
            old_sample_info_path = self.sample_info.path
            new_sample_info_path = default_storage.path(new_sample_info_name)
            os.rename(old_sample_info_path, new_sample_info_path)
            self.sample_info.name = new_sample_info_name
            super().save(update_fields=['sample_info'])

        # Rename and save the supplementary_file if the file name has changed
        new_supplementary_file_name = self.get_supplementary_file_upload_path(
            self.supplementary_file.name if self.supplementary_file else None)
        if (self.supplementary_file and new_supplementary_file_name and
                self.supplementary_file.name != new_supplementary_file_name):

            old_supplementary_file_path = self.supplementary_file.path
            new_supplementary_file_path = default_storage.path(
                new_supplementary_file_name)
            os.rename(old_supplementary_file_path, new_supplementary_file_path)
            self.supplementary_file.name = new_supplementary_file_name
            super().save(update_fields=['supplementary_file'])


@receiver(post_delete, sender=Sample)
def delete_sample_info(sender, instance, **kwargs):
    if instance.sample_info:
        if default_storage.exists(instance.sample_info.name):
            default_storage.delete(instance.sample_info.name)


@receiver(post_delete, sender=Sample)
def delete_supplementary_file(sender, instance, **kwargs):
    if instance.supplementary_file:
        if default_storage.exists(instance.supplementary_file.name):
            default_storage.delete(instance.supplementary_file.name)


class Experiment(models.Model):
    sample = models.ForeignKey(
        Sample, on_delete=models.PROTECT, related_name="experiments")
    method = models.ForeignKey(
        Method, on_delete=models.PROTECT, related_name="experiments")
    staff = models.ForeignKey(
        Staff, on_delete=models.PROTECT, related_name="experiments")
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="experiments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255, help_text="free text field")
    date_created = models.DateField(help_text="when was the data created")
    # file name is defined by function get_experiment_file_upload_path below
    # the actual file path information is updated on the model instance after
    # creation, because the PK can only be used after creation
    experiment_file = models.FileField(upload_to="experiment_files",
                                       verbose_name="experimental data file path")
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    def get_experiment_file_upload_path(self, filename):
        # Use the instance's primary key as the new file name
        new_filename = f"{self.pk}.zip"
        return os.path.join('experiment_files', new_filename)

    def save(self, *args, **kwargs):
        # Save the instance to generate the primary key (if it's a new instance)
        is_new = self._state.adding
        super().save(*args, **kwargs)

        # Save the file into the new path and name created with the primary key
        if is_new and self.experiment_file:
            old_file_path = self.experiment_file.path
            new_file_name = self.get_experiment_file_upload_path(
                self.experiment_file.name)
            new_file_path = default_storage.path(new_file_name)
            os.rename(old_file_path, new_file_path)
            self.experiment_file.name = new_file_name
            super().save(update_fields=['experiment_file'])


@receiver(post_delete, sender=Experiment)
def delete_experiment_file(sender, instance, **kwargs):
    if instance.experiment_file:
        if default_storage.exists(instance.experiment_file.name):
            default_storage.delete(instance.experiment_file.name)
