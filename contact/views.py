from django.conf import settings
from django.shortcuts import redirect, render
from .models import Contact
from django.core.mail import EmailMessage, mail_admins, send_mail
from django.template.loader import get_template
from django.urls import reverse
from django.contrib import messages

def contactview(request):

    if request.method == 'POST':
        name= request.POST.get("fullname")
        email= request.POST.get("email")
        subject= request.POST.get("subject")
        message=request.POST.get("message")
        contact = Contact.objects.create(fullname=name, email=email, subject=subject, message=message)
        contact.save()

        subject= str(email) + " > " + subject
        
        template = get_template('contact_form.txt')
        content = template.render({'name': name, 'email': email, 'message': message})


        message = "Subject: From > {} {}\n\nMessage: {}".format(subject, email, message)
        # mail_admins(subject, message)
        email = EmailMessage(subject, content, 'Edumy ', [settings.EMAIL_HOST_USER], headers={'Reply to': email})
        email.send()
        # send_mail(subject, message, email, [settings.EMAIL_HOST_USER])

        messages.success(request, 'Message sent Successfully.')
        return redirect(reverse('contact'))

    else:
        return render(request, 'contact.html')