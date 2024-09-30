from users.models import CustomUser
from users.serializers import PublicDeveloperSerializer, PrivateDeveloperSerializer
from projects.models import Session
from rest_framework.exceptions import ValidationError


class DeveloperDataService:
    def __init__(self, session_id, developer_id):
        self.session_id = session_id
        self.developer_id = developer_id

    def get_developer_data(self, public=True):
        try:
            session = Session.objects.get(id=self.session_id)
            developer = CustomUser.objects.get(id=self.developer_id)

            if public or developer not in session.participants.all():
                return PublicDeveloperSerializer(developer).data
            else:
                return PrivateDeveloperSerializer(developer).data

        except Session.DoesNotExist:
            raise ValidationError("Session not found")
        except CustomUser.DoesNotExist:
            raise ValidationError("Developer not found")
        except Exception as e:
            raise ValidationError(f"Error retrieving developer data: {str(e)}")
