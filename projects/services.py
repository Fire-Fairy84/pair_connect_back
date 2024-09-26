from rest_framework.exceptions import ValidationError


def inherit_level_from_project(session):
    try:
        session.level = session.project.level
    except Exception as e:
        raise ValidationError(f"Error inheriting level from project: {e}")


def validate_and_assign_stack(session):
    try:
        project_stack = session.project.stack
        session_stack = session.stack

        if project_stack.name != 'Fullstack':
            if not session_stack or session_stack != project_stack:
                raise ValidationError(
                    f"Invalid stack. For this project, the session must use stack {project_stack.name}.")
        else:
            if session_stack.name not in ['Fullstack', 'Backend', 'Frontend']:
                raise ValidationError("Invalid stack choice. You can only choose Fullstack, Backend, or Frontend.")
    except Exception as e:
        raise ValidationError(f"Error validating or assigning stack: {e}")
