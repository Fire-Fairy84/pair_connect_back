from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


class EmailService:
    @staticmethod
    def send_invite_email(session, developer):
        try:
            subject = f"¡{session.project.owner.name} te invita a una sesión de programación!"

            context = {
                'developer_name': developer.name,
                'owner_name': session.project.owner.name,
                'session_description': session.description,
                'session_date': session.schedule_date_time.strftime("%d-%m-%Y %H:%M"),
                'session_link': session.session_link or "http://localhost:5173",
            }

            html_content = render_to_string('emails/invite_developer_email.html', context)
            text_content = render_to_string('emails/invite_developer_email.txt', context)

            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [developer.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

        except Exception as e:
            raise Exception(f"Error sending invite email: {str(e)}")

