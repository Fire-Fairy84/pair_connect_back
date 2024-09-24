from djoser.email import ActivationEmail as BaseActivationEmail
from django.template.loader import render_to_string


class ActivationEmail(BaseActivationEmail):
    template_name = 'emails/activation_email.html'
    template_txt_name = 'emails/activation_email.txt'
    subject = "Activate Your Account, {user.username}!"

    def get_context_data(self):
        context = super().get_context_data()
        context['user'] = self.user
        context['activation_url'] = self.context.get('activation_url')
        return context

    def send(self, to, **kwargs):
        try:
            # Format the subject with the user's username
            subject = self.subject.format(user=self.user)

            # Get the context data for rendering templates
            context = self.get_context_data()

            # Render the HTML and plain text content
            html_content = render_to_string(self.template_name, context)
            text_content = render_to_string(self.template_txt_name, context)

            # Assign the recipient and subject
            self.to = to
            self.subject = subject

            # Assign the plain text content to body
            self.body = text_content

            # Attach the HTML content as an alternative
            self.attach_alternative(html_content, "text/html")

            # Send the email using the parent class's send method
            super().send(to, **kwargs)
        except Exception as e:
            # Log the exception or handle it as needed
            print(f"Failed to send activation email to {to}: {e}")
            raise
