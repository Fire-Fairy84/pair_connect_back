from rest_framework.exceptions import ValidationError

from projects.models import InterestedParticipant, Session
from users.models import CustomUser
from users.serializers import PrivateDeveloperSerializer, PublicDeveloperSerializer

from .models import CustomUser


class UserProfileService:
    def __init__(self, viewer, user_id):
        """
        :param viewer: user viewing the profile
        :param user_id: the id of the user who's profile is being viewed
        """
        self.viewer = viewer
        self.user_id = user_id

    def get_profile_data(self, session=None):
        """
            Retrieves a user's profile data based on the provided session.
        Args:
            session (Session, optional): The session for which the user's interest is checked. Defaults to None.
        Returns:
            dict: The user's profile data.
        Raises:
            ValidationError: If the user is not found or an error occurs while retrieving the profile data.
        """
        try:
            user = CustomUser.objects.get(id=self.user_id)
            if not session:
                return {
                    "profile_data": PublicDeveloperSerializer(user).data,
                    "has_permission": False,
                }

            is_interested = InterestedParticipant.objects.filter(
                user=user, session=session
            ).exists()

            print(
                f"User being viewed: {user.username}, Session: {session.id}, Is Interested: {is_interested}"
            )

            if is_interested:
                return {
                    "profile_data": PrivateDeveloperSerializer(user).data,
                    "has_permission": True,
                }

            return {
                "profile_data": PublicDeveloperSerializer(user).data,
                "has_permission": False,
            }

        except CustomUser.DoesNotExist:
            raise ValidationError("User not found")

        except Exception as e:
            raise ValidationError(f"Error retrieving user profile: {str(e)}")
