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
            now = timezone.now()
            user_stack = self.user.stack
            user_level = self.user.level
            user_languages = list(self.user.prog_language.all())

            # Debug: Print user attributes
            print(f"User ID: {self.user.id}")
            print(f"User Stack: {user_stack.name if user_stack else 'None'}")
            print(f"User Level: {user_level.name if user_level else 'None'}")
            print(f"User Languages: {[lang.name for lang in user_languages]}")
            print("-" * 50)

            # Define stack compatibility based on user's stack
            stack_compatible = self.get_stack_compatibility(user_stack)
            # Debug: Print stack compatibility
            print(
                f"Compatible Stacks for User's Stack '{user_stack.name if user_stack else 'None'}': {stack_compatible}")
            print("-" * 50)

            # Base queryset: Exclude user's own sessions and past sessions
            sessions = Session.objects.exclude(host=self.user).filter(schedule_date_time__gte=now)
            # Debug: Print count after excluding user's own sessions and past sessions
            print(f"Sessions after excluding user's own and past sessions: {sessions.count()}")

            # Filter sessions that have at least one common language
            if user_languages:
                language_filter = Q(languages__in=user_languages)
                sessions = sessions.filter(language_filter).distinct()
                # Debug: Print count after language filtering
                print(f"Sessions after language filtering: {sessions.count()}")
                print("-" * 50)
            else:
                # If the user has no languages, no sessions can be suggested based on languages
                print("User has no programming languages specified. No sessions to suggest based on languages.")
                print("-" * 50)
                return Session.objects.none()

            # Annotate each session with a priority based on matching criteria
            sessions = sessions.annotate(
                priority=Case(
                    # Round 1: Same level, compatible stack
                    When(
                        Q(level=user_level) & Q(stack__name__in=stack_compatible),
                        then=1
                    ),
                    # Round 2: Compatible stack only
                    When(
                        Q(stack__name__in=stack_compatible),
                        then=2
                    ),
                    # Round 3: Only language match (handled by default)
                    default=3,
                    output_field=IntegerField()
                )
            )

            # Filter out sessions that don't match any of the three rounds
            sessions = sessions.filter(priority__lte=3)
            # Debug: Print count after filtering by priority
            print(f"Sessions after filtering by priority (<=3): {sessions.count()}")
            print("-" * 50)

            # Order by priority and then by nearest date_time
            sessions = sessions.order_by('priority', 'schedule_date_time')

            # Debug: Print ordered sessions with detailed info
            print("Ordered Sessions with Details:")
            print("-" * 50)
            ordered_sessions = sessions.select_related('level', 'stack').prefetch_related('languages').distinct()[:10]
            for session in ordered_sessions:
                languages = [lang.name for lang in session.languages.all()]
                print(f"Session ID: {session.id}")
                print(f"  Name: {session.name}")
                print(f"  Priority: {session.priority}")
                print(f"  Schedule DateTime: {session.schedule_date_time}")
                print(f"  Level: {session.level.name if session.level else 'None'}")
                print(f"  Stack: {session.stack.name if session.stack else 'None'}")
                print(f"  Languages: {languages}")
                print("-" * 50)

            return sessions

        except Exception as e:
            raise ValidationError(f"Error retrieving suggested sessions: {str(e)}")

    def get_stack_compatibility(self, user_stack):
        """
        Returns a list of compatible stack names based on the user's stack.
        """
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
