from django.db.models import Q, Case, When, IntegerField
from django.utils import timezone
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

            interested_user_ids = InterestedParticipant.objects.filter(session=self.session).values_list('user_id',
                                                                                                         flat=True)
            participant_user_ids = self.session.participants.values_list('id', flat=True)

            host_user = self.session.host
            host_user_id = host_user.id if host_user else None

            excluded_user_ids = list(interested_user_ids) + list(participant_user_ids)
            if host_user_id:
                excluded_user_ids.append(host_user_id)

            stack_filter = Q()
            if session_stack_name == 'Fullstack':
                stack_filter = Q(stack__name='Fullstack') | Q(stack__name='Frontend') | Q(stack__name='Backend')
            elif session_stack_name == 'Frontend':
                stack_filter = Q(stack__name='Frontend') | Q(stack__name='Fullstack')
            elif session_stack_name == 'Backend':
                stack_filter = Q(stack__name='Backend') | Q(stack__name='Fullstack')

            if session_stack_name == 'Frontend':
                stack_filter &= ~Q(stack__name='Backend')
            elif session_stack_name == 'Backend':
                stack_filter &= ~Q(stack__name='Frontend')

            language_filter = Q()
            for language_name in session_language_names:
                language_filter |= Q(prog_language__name=language_name)

            phase1_users = CustomUser.objects.exclude(
                id__in=excluded_user_ids
            ).filter(
                stack_filter,
                level__name=session_level_name,
                is_staff=False,
                prog_language__isnull=False,
                stack__isnull=False
            ).filter(language_filter).distinct()

            if phase1_users.count() >= 5:
                return phase1_users

            phase2_users = CustomUser.objects.exclude(
                id__in=excluded_user_ids
            ).filter(
                stack_filter,
                is_staff=False,
                prog_language__isnull=False,
                stack__isnull=False
            ).filter(language_filter).distinct()

            combined_users = list(phase1_users) + [user for user in phase2_users if user not in phase1_users]

            if len(combined_users) >= 5:
                return combined_users[:5]

            phase3_users = CustomUser.objects.exclude(
                id__in=excluded_user_ids
            ).filter(
                stack_filter,
                is_staff=False,
                stack__isnull=False
            ).distinct()

            final_users = combined_users + [user for user in phase3_users if user not in combined_users]

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
            now = timezone.now()
            user_stack = self.user.stack
            user_level = self.user.level
            user_languages = list(self.user.prog_language.all())

            stack_compatible = self.get_stack_compatibility(user_stack)
            sessions = Session.objects.exclude(host=self.user).filter(schedule_date_time__gte=now)

            if user_languages:
                language_filter = Q(languages__in=user_languages)
                sessions = sessions.filter(language_filter).distinct()
            else:
                return Session.objects.none()

            sessions = sessions.annotate(
                priority=Case(
                    When(
                        Q(level=user_level) & Q(stack__name__in=stack_compatible),
                        then=1
                    ),
                    When(
                        Q(stack__name__in=stack_compatible),
                        then=2
                    ),
                    default=3,
                    output_field=IntegerField()
                )
            )

            sessions = sessions.filter(priority__lte=3)
            sessions = sessions.order_by('priority', 'schedule_date_time')
            suggested_sessions = sessions.select_related('level', 'stack').prefetch_related('languages').distinct()[:10]

            return suggested_sessions

        except Exception as e:
            raise ValidationError(f"Error retrieving suggested sessions: {str(e)}")

    def get_stack_compatibility(self, user_stack):
        stack_mapping = {
            'Fullstack': ['Fullstack', 'Frontend', 'Backend'],
            'Frontend': ['Frontend', 'Fullstack'],
            'Backend': ['Backend', 'Fullstack'],
        }
        stack_mapping.get(user_stack, [])
        return stack_mapping.get(user_stack, [])


class SessionCreationService:
    @staticmethod
    def handle_create_session(user, project_id, session_data):
        try:
            project = Project.objects.get(id=project_id)

            if project.owner != user:
                raise PermissionDenied("Only the owner of the project can create sessions.")

            session_data.pop('project', None)
            languages = session_data.pop('languages', None)
            is_private = session_data.pop('is_private', None)
            if is_private is not None:
                session_data['public'] = not is_private

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
