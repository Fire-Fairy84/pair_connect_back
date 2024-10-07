from rest_framework.exceptions import ValidationError, PermissionDenied
from users.models import CustomUser
from .email_service import EmailService
from projects.models import Session, Project


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
        try:
            session_stack = self.session.stack
            session_level = self.session.level
            session_languages = list(self.session.languages.all())
            suggested_users = CustomUser.objects.filter(stack=session_stack)

            if session_languages:
                suggested_users = suggested_users.filter(prog_language__in=session_languages).distinct()

            if session_level:
                suggested_users = suggested_users.filter(level=session_level)

            return suggested_users

        except CustomUser.DoesNotExist:
            raise ValidationError("No developers found matching the criteria.")
        except ValidationError as e:
            raise ValidationError(f"Validation error: {str(e)}")
        except Exception as e:
            raise ValidationError(f"An unexpected error occurred: {str(e)}")


class InvitationService:
    def __init__(self, session, developer):
        self.session = session
        self.developer = developer

    def send_invitation(self):
        try:
            EmailService.send_invite_email(self.session, self.developer)
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
            if user_stack == 'Fullstack':
                suggested_sessions = Session.objects.all()
            elif user_stack == 'Frontend':
                suggested_sessions = Session.objects.filter(stack__in=['Frontend', 'Fullstack'])
            elif user_stack == 'Backend':
                suggested_sessions = Session.objects.filter(stack__in=['Backend', 'Fullstack'])

            if user_languages:
                suggested_sessions = suggested_sessions.filter(languages__in=user_languages).distinct()

            if user_level:
                suggested_sessions = suggested_sessions.filter(level=user_level)

            return suggested_sessions
        except Exception as e:
            raise ValidationError(f"Error retrieving suggested sessions: {str(e)}")


class SessionCreationService:
    @staticmethod
    def handle_create_session(user, project_id, session_data):
        try:
            project = Project.objects.get(id=project_id)

            if project.owner != user:
                raise PermissionDenied("Only the owner of the project can create sessions.")

            session_data.pop('project', None)
            languages = session_data.pop('languages', None)

            session = Session.objects.create(
                project=project,
                host=user,
                level=project.level,
                **session_data
            )

            if languages:
                session.languages.set(languages)

            return session

        except Project.DoesNotExist:
            raise PermissionDenied("Project does not exist.")
        except Exception as e:
            raise PermissionDenied(f"An error occurred: {str(e)}")
