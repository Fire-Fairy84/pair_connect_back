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


# from djoser.email import ActivationEmail as BaseActivationEmail
# from django.template.loader import render_to_string
# from users.models import CustomUser as User 
# from django.utils.http import urlsafe_base64_decode



# class ActivationEmail(BaseActivationEmail):
#     template_name = 'emails/activation_email.html'
#     template_txt_name = 'emails/activation_email.txt'
#     subject = "Activate Your Account, {user.username}!"

#     def get_context_data(self):
#         context = super().get_context_data()

#         # Verifica se uid e token sono presenti
#         uid = self.context.get('uid')
#         token = self.context.get('token')

#         if not uid or not token:
#             raise ValueError("UID or token not found in the context.")

#         # Decodifica il uid per ottenere l'ID dell'utente
#         try:
#             user_id = urlsafe_base64_decode(uid).decode()
#             user = User.objects.get(pk=user_id)
#         except (User.DoesNotExist, ValueError, TypeError) as e:
#             raise ValueError(f"Error decoding UID or fetching user: {e}")

#         # Aggiungi l'utente e il link di attivazione al contesto
#         context['user'] = user
#         frontend_url = "http://localhost:3000"
#         context['activation_url'] = f"{frontend_url}/activate/{uid}/{token}"

#         return context

#     def send(self, to, **kwargs):
#         try:
#             context = self.get_context_data()
#             subject = self.subject.format(user=context['user'])

#             html_content = render_to_string(self.template_name, context)
#             text_content = render_to_string(self.template_txt_name, context)

#             self.to = to
#             self.subject = subject
#             self.body = text_content

#             self.attach_alternative(html_content, "text/html")
#             super().send(to, **kwargs)
#         except Exception as e:
#             print(f"Failed to send activation email to {to}: {e}")
#             raise