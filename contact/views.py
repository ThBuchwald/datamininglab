from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import ContactForm

# Create your views here.

def contact_view (request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'] 
            email = form.cleaned_data['email']
            subject = "Contact Form"
            message = f"{name} ({email}) sent the follwowing message:\n\n{form.cleaned_data['message']}"
            send_mail(subject, 
                      message, 
                      email, 
                      ['datamininglabfreiberg@gmail.com'])
            return redirect('success')
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})

def success_view (request):
    return render(request, 'contact/success.html')