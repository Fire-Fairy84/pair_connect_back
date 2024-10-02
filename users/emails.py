from djoser.email import ActivationEmail as BaseActivationEmail
from django.template.loader import render_to_string


class ActivationEmail(BaseActivationEmail):
    template_name = 'emails/activation_email.html'
    template_txt_name = 'emails/activation_email.txt'
    subject = "Activate Your Account, {user.username}!"

    def get_context_data(self):
        context = super().get_context_data()
        context['user'] = self.user
        
        frontend_url = "http://localhost:3000"  # URL del frontend
        context['activation_url'] = f"{frontend_url}/activate/{self.context.get('uid')}/{self.context.get('token')}"
        # context['activation_url'] = self.context.get('activation_url')
        return context

    def send(self, to, **kwargs):
        try:
            subject = self.subject.format(user=self.user)

            context = self.get_context_data()

            html_content = render_to_string(self.template_name, context)
            text_content = render_to_string(self.template_txt_name, context)

            self.to = to
            self.subject = subject

            self.body = text_content

            self.attach_alternative(html_content, "text/html")

            super().send(to, **kwargs)
        except Exception as e:
            print(f"Failed to send activation email to {to}: {e}")
            raise
