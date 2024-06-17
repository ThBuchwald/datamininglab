from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from main.models import Institute, Staff, Method, FundingBody, Project, SampleType, Sample, Experiment

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
            'fields': ('username', 'email', 'institute', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # This checks if it's a new user
            # Create a password reset token
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(obj)
            uid = urlsafe_base64_encode(force_bytes(obj.pk))
            
            # Build the password reset URL
            password_reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            print(f'Welcome, {obj.first_name}! Please set up your password by visiting this link: {password_reset_link}')

            # Send an email with the password reset link
            send_mail(
                'Your New Account at DataMiningLabFreiberg',
                f'Welcome, {obj.first_name}! Please set up your password by visiting this link: {password_reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [obj.email],
                fail_silently=False,
            )

# Register other models here
admin.site.register(Institute)
admin.site.register(Staff)
admin.site.register(Method)
admin.site.register(FundingBody)
admin.site.register(Project)
admin.site.register(SampleType)
admin.site.register(Sample)
admin.site.register(Experiment)
