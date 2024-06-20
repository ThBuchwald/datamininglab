from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings

# this function is used in admin.py and forms.py when a new user is created
def send_initial_reset_email(request, user):
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    password_reset_link = request.build_absolute_uri(
        reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    )

    group_names = ", ".join([group.name for group in user.groups.all()])
    institute_names = ", ".join([institute.name for institute in user.institute.all()])

    subject = 'Set Up Your DMLF Password'
    message = (
        f'Hello {user.first_name},\n\n'
        f'welcome to the Data Mining Lab Freiberg! A new account has been set up for you.\n\n'
        f'Your user name is: {user.username}\n'
        f'You belong to the following user categories: {group_names}\n'
        f'You belong to the following institutes: {institute_names}\n\n'
        f'Please set up your account password by visiting the following link:\n{password_reset_link}\n\n'
        f'Welcome to the Data Mining Lab Freiberg!'
    )
    print(message)
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email, "datamininglabfreiberg@gmail.com"]
    send_mail(subject, message, email_from, recipient_list, fail_silently=False)
