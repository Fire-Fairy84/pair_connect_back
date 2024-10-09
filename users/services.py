from rest_framework.exceptions import ValidationError

from projects.models import InterestedParticipant, Session
from users.models import CustomUser
from users.serializers import PrivateDeveloperSerializer, PublicDeveloperSerializer

from .models import CustomUser

# class DeveloperDataService:
#     def __init__(self, session_id, developer_id):
#         self.session_id = session_id
#         self.developer_id = developer_id

#     def get_developer_data(self, public=True):
#         try:
#             session = Session.objects.get(id=self.session_id)
#             developer = CustomUser.objects.get(id=self.developer_id)

#             if public or developer not in session.participants.all():
#                 return PublicDeveloperSerializer(developer).data
#             else:
#                 return PrivateDeveloperSerializer(developer).data

#         except Session.DoesNotExist:
#             raise ValidationError("Session not found")
#         except CustomUser.DoesNotExist:
#             raise ValidationError("Developer not found")
#         except Exception as e:
#             raise ValidationError(f"Error retrieving developer data: {str(e)}")


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
                return PublicDeveloperSerializer(user).data

            if InterestedParticipant.objects.filter(
                user=self.viewer, session=session
            ).exists():
                return PrivateDeveloperSerializer(user).data

            return PublicDeveloperSerializer(user).data

        except CustomUser.DoesNotExist:
            raise ValidationError("User not found")

        except Exception as e:
            raise ValidationError(f"Error retrieving user profile: {str(e)}")
