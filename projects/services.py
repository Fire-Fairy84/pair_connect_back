from rest_framework.exceptions import ValidationError
from users.models import CustomUser


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
        session_languages = list(self.session.languages.all())  # Convertir a lista de objetos relacionados

        print(f"Languages: {session_languages}")  # Para depuración

        # Filtro inicial por stack
        if session_stack.name == 'Fullstack':
            # Sugerimos todos los desarrolladores con Fullstack
            suggested_users = CustomUser.objects.filter(stack=session_stack)
        else:
            # Filtramos por stack específico
            suggested_users = CustomUser.objects.filter(stack=session_stack)

        # Filtrar por lenguajes de programación
        if session_languages:
            suggested_users = suggested_users.filter(prog_language__in=session_languages).distinct()

        # Filtrar por nivel
        if session_level:
            suggested_users = suggested_users.filter(level=session_level)

        return suggested_users

