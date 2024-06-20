from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from main.models import Institute, Staff, Method, FundingBody, Project, SampleType, Sample, Experiment
from main.utils.email_utils import send_initial_reset_email

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Institutes', {'fields': ('institute',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'groups', 'institute', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # New user
            obj.set_unusable_password()
            obj.save()
            send_initial_reset_email(request, obj)

# Register other models here
admin.site.register(Institute)
admin.site.register(Staff)
admin.site.register(Method)
admin.site.register(FundingBody)
admin.site.register(Project)
admin.site.register(SampleType)
admin.site.register(Sample)
admin.site.register(Experiment)
