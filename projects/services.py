from django.db.models import Q
from rest_framework.exceptions import ValidationError, PermissionDenied
from users.models import CustomUser
from .email_service import EmailService
from projects.models import Session, Project, InterestedParticipant


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
            session_stack_name = self.session.stack.name
            session_level_name = self.session.level.name if self.session.level else None
            session_language_names = list(self.session.languages.values_list('name', flat=True))

            print(
                f"Session Stack: {session_stack_name}, Level: {session_level_name}, Languages: {session_language_names}")

            interested_user_ids = InterestedParticipant.objects.filter(session=self.session).values_list('user_id',
                                                                                                         flat=True)
            print(f"Interested User IDs: {list(interested_user_ids)}")

            # Define the stack filter using names
            stack_filter = Q()
            if session_stack_name == 'Fullstack':
                stack_filter = Q(stack__name='Fullstack') | Q(stack__name='Frontend') | Q(stack__name='Backend')
            elif session_stack_name == 'Frontend':
                stack_filter = Q(stack__name='Frontend') | Q(stack__name='Fullstack')
            elif session_stack_name == 'Backend':
                stack_filter = Q(stack__name='Backend') | Q(stack__name='Fullstack')

            # Exclude incompatible stacks
            if session_stack_name == 'Frontend':
                stack_filter &= ~Q(stack__name='Backend')
            elif session_stack_name == 'Backend':
                stack_filter &= ~Q(stack__name='Frontend')

            # Phase 1: Match stack, level, and at least one language
            language_filter = Q()
            for language_name in session_language_names:
                language_filter |= Q(prog_language__name=language_name)

            phase1_users = CustomUser.objects.exclude(
                id__in=interested_user_ids
            ).filter(
                stack_filter,
                level__name=session_level_name,
                is_staff=False,
                prog_language__isnull=False,
                stack__isnull=False
            ).filter(language_filter).distinct()

            print(f"Phase 1 Users: {list(phase1_users.values('id', 'username', 'stack__name', 'prog_language__name'))}")

            if phase1_users.count() >= 5:
                return phase1_users

            # Phase 2: Relax the level filter
            phase2_users = CustomUser.objects.exclude(
                id__in=interested_user_ids
            ).filter(
                stack_filter,
                is_staff=False,
                prog_language__isnull=False,
                stack__isnull=False
            ).filter(language_filter).distinct()

            print(f"Phase 2 Users: {list(phase2_users.values('id', 'username', 'stack__name', 'prog_language__name'))}")

            combined_users = list(phase1_users) + [user for user in phase2_users if user not in phase1_users]

            if len(combined_users) >= 5:
                return combined_users[:5]

            # Phase 3: Relax the language filter
            phase3_users = CustomUser.objects.exclude(
                id__in=interested_user_ids
            ).filter(
                stack_filter,
                is_staff=False,
                stack__isnull=False
            ).distinct()

            print(f"Phase 3 Users: {list(phase3_users.values('id', 'username', 'stack__name', 'prog_language__name'))}")

            final_users = combined_users + [user for user in phase3_users if user not in combined_users]

            print(f"Final Suggested Users: {list(final_users)}")

            return final_users[:5]

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


class InterestNotificationService:
    def __init__(self, session, interested_user):
        self.session = session
        self.interested_user = interested_user

    def send_notification(self):
        try:
            EmailService.send_interest_notification_email(self.session, self.interested_user)
        except Exception as e:
            raise ValidationError(f"Failed to send interest notification: {str(e)}")


class ConfirmationNotificationService:
    def __init__(self, session, developer):
        self.session = session
        self.developer = developer

    def send_confirmation(self):
        try:
            EmailService.send_confirmation_email(self.session, self.developer)
        except Exception as e:
            raise ValidationError(f"Failed to send confirmation email: {str(e)}")


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
