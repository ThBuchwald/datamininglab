from django.contrib import admin
from main.models import User, Institute, Staff, Method, FundingBody, Project, SampleType, Sample, Experiment

# Register your models here.
admin.site.register(User)
admin.site.register(Institute)
admin.site.register(Staff)
admin.site.register(Method)
admin.site.register(FundingBody)
admin.site.register(Project)
admin.site.register(SampleType)
admin.site.register(Sample)
admin.site.register(Experiment)
