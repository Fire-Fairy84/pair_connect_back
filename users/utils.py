from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator


def send_confirmation_email(user, token, request):
    # confirmation_url = request.build_absolute_uri(
    #     f"/api/auth/users/activation/?token={token}"
    # )
    
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


