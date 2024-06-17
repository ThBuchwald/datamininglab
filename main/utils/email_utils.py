from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings

def send_password_reset_email(request, user):
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    password_reset_link = request.build_absolute_uri(
        reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    )

    subject = 'Set Up Your DMLF Password'
    message = f'Hello {user.first_name},\n\nwelcome to the Data Mining Lab Freiberg!\nA new account has been set up for you.\n\nYour user name is: {user.username}\nPlease set up your account password by visiting the following link:\n{password_reset_link}\n\nWelcome to the Data Mining Lab Freiberg!'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email, "datamininglabfreiberg@gmail.com"]
    send_mail(subject, message, email_from, recipient_list, fail_silently=False)