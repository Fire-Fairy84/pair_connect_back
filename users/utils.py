from django.template.loader import render_to_string
from django.core.mail import EmailMessage


def send_confirmation_email(user, token, request):
    frontend_url = "http://localhost:3000" 
    confirmation_url = f"{frontend_url}/activate/{user.uid}/{token}/"

    email_subject = 'Confirm Your Email Address'
    email_body = render_to_string('confirmation_email.html', {
        'user': user,
        'confirmation_url': confirmation_url,
    })

    email = EmailMessage(
        email_subject,
        email_body,
        to=[user.email]
    )

    email.send()


