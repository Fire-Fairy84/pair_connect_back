from rest_framework.exceptions import ValidationError
from users.models import CustomUser
from .utils import send_email
from projects.models import Session


class SessionService:
    def __init__(self, session):
        self.session = session

    def inherit_level_from_project(self):
        try:
            self.session.level = self.session.project.level
        except Exception as e:
            raise ValidationError(f"Error inheriting level from project: {e}")

    def validate_and_assign_stack(self):
        try:
            project_stack = self.session.project.stack
            session_stack = self.session.stack

            if project_stack.name != 'Fullstack':
                if not session_stack or session_stack != project_stack:
                    raise ValidationError(
                        f"Invalid stack. For this project, the session must use stack {project_stack.name}.")
            else:
                if session_stack.name not in ['Fullstack', 'Backend', 'Frontend']:
                    raise ValidationError("Invalid stack choice. You can only choose Fullstack, Backend, or Frontend.")
        except Exception as e:
            raise ValidationError(f"Error validating or assigning stack: {e}")


class DeveloperSuggestionService:

    def __init__(self, session):
        self.session = session

    def get_suggested_developers(self):
        session_stack = self.session.stack
        session_level = self.session.level
        session_languages = list(self.session.languages.all())

        if session_stack.name == 'Fullstack':
            suggested_users = CustomUser.objects.filter(stack=session_stack)
        else:
            suggested_users = CustomUser.objects.filter(stack=session_stack)

        if session_languages:
            suggested_users = suggested_users.filter(prog_language__in=session_languages).distinct()

        if session_level:
            suggested_users = suggested_users.filter(level=session_level)

        return suggested_users


class InvitationService:
    def __init__(self, session, developer):
        self.session = session
        self.developer = developer

    def send_invitation(self):
        try:
            project_owner_name = self.session.project.owner.name
            subject = f"¡{project_owner_name} te invita a una sesión de programación!"
            message = (
                f"¡Hola {self.developer.name}!\n\n"
                f"{project_owner_name} te ha invitado a unirte a la sesión '{self.session.description}' que se "
                f"llevará a cabo el {self.session.schedule_date_time}."
                f"¡Va a estar genial, vamos a programar y aprender juntos!\n\n"
                f"Puedes ver toda la info de la sesión a través de este enlace: {self.session.session_link}.\n\n"
                f"Nos vemos ahí y no olvides traer tus ganas de aprender y programar, ¡será divertido!\n\n"
                f"Un saludo,\n"
                f"El equipo de Pair Connect"
            )
            send_email(subject, message, self.developer.email)
        except Exception as e:
            raise ValidationError(f"Failed to send invitation: {str(e)}")


class SessionSuggestionService:

    def __init__(self, user):
        self.user = user

    def get_suggested_sessions(self):
        try:
            user_stack = self.user.stack
            user_level = self.user.level
            user_languages = list(self.user.prog_language.all())

            suggested_sessions = Session.objects.filter(stack=user_stack)

            if user_languages:
                suggested_sessions = suggested_sessions.filter(languages__in=user_languages).distinct()

            if user_level:
                suggested_sessions = suggested_sessions.filter(level=user_level)

            return suggested_sessions
        except Exception as e:
            raise ValidationError(f"Error retrieving suggested sessions: {str(e)}")