from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import ContactForm

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'] 
            email = form.cleaned_data['email']  # This is the email from the user
            subject = "Contact Form"
            message = f"{name} ({email}) sent the following message:\n\n{form.cleaned_data['message']}"
            
            # Define your sender email from your verified domain
            sender_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = ['datamininglabfreiberg@gmail.com']  # Your receiving email address

            # Create EmailMessage object which allows more customization
            mail = EmailMessage(
                subject,
                message,
                sender_email,  # From email (your verified domain email)
                recipient_list,
                reply_to=[email],  # Add user's email in reply-to for direct replies
            )
            mail.send()

            return redirect('success')
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})

def success_view(request):
    return render(request, 'contact/success.html')
