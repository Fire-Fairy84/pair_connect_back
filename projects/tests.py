import pytest
from rest_framework import status
from projects.serializers import ProjectSerializer
from users.models import CustomUser
from projects.models import Project, Session
from skills.models import Stack, Level, ProgLanguage
from datetime import datetime
from django.urls import reverse



def authenticate_client(client, user):
    """
    Authenticate the client using JWT for a given user.
    """
    response = client.post('/api/auth/jwt/create/', {'email': user.email, 'password': 'password123'})
    token = response.data['access']
    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'


@pytest.mark.django_db
def test_project_creation_success(client):
    """
    Scenario: Successful project creation
    Given I am an authenticated user
    When I create a new project with valid data
    Then the project should be created successfully
    """
    # Given: I am an authenticated user
    user = CustomUser.objects.create_user(
        username='testuser', email='testuser@example.com', password='password123'
    )
    authenticate_client(client, user)

    # When: I create a new project
    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    url = '/api/projects/projects/'
    data = {
        'name': 'Test Project',
        'description': 'A new project',
        'stack': stack.id,
        'level': level.id,
        'languages': [prog_language.id],
    }
    response = client.post(url, data)

    # Then: The project should be created successfully
    assert response.status_code == status.HTTP_201_CREATED
    assert Project.objects.filter(name='Test Project').exists()


@pytest.mark.django_db
def test_get_suggested_developers_success(client):
    """
    Scenario: Successful retrieval of suggested developers
    Given there is an existing session
    And I am authenticated
    When I request suggested developers for the session
    Then I should receive a list of suggested developers
    """
    # Given: I am an authenticated user
    user = CustomUser.objects.create_user(
        username='owner', email='owner@example.com', password='password123'
    )
    authenticate_client(client, user)

    # And: There is an existing session
    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    project = Project.objects.create(owner=user,
                                     name='Test Project',
                                     stack=stack,
                                     level=level)
    project.languages.add(prog_language)

    session = Session.objects.create(
        project=project,
        host=user,
        description='Test Session',
        stack=stack,
        level=level,
        schedule_date_time=datetime.now()
    )
    session.languages.add(prog_language)

    # When: I request suggested developers
    url = f'/api/projects/sessions/{session.id}/suggested-developers/'
    response = client.get(url)

    # Then: I should receive a list of suggested developers
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_invite_developer_to_session_success(client):
    """
    Scenario: Successful invitation of a developer to a session
    Given I am the owner of a session
    And a developer exists
    When I invite the developer to the session
    Then the developer should receive an invitation email
    """
    # Given: I am the owner of a session
    user = CustomUser.objects.create_user(
        username='owner',
        email='owner@example.com',
        password='password123'
    )
    authenticate_client(client, user)

    # And: A developer exists
    developer = CustomUser.objects.create_user(
        username='developer',
        email='developer@example.com',
        password='password123'
    )

    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    project = Project.objects.create(owner=user,
                                     name='Test Project',
                                     stack=stack,
                                     level=level)
    project.languages.add(prog_language)

    session = Session.objects.create(project=project,
                                     host=user,
                                     description='Test Session',
                                     stack=stack,
                                     level=level,
                                     schedule_date_time=datetime.now())
    session.languages.add(prog_language)

    # When: I invite the developer to the session
    url = f'/api/projects/sessions/{session.id}/developers/{developer.id}/invite/'
    response = client.post(url)

    # Then: The developer should receive an invitation
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_suggested_sessions_for_user_success(client):
    """
    Scenario: Successful retrieval of suggested sessions for a user
    Given I am an authenticated developer
    When I request suggested sessions
    Then I should receive a list of sessions that match my skills
    """
    # Given: I am an authenticated developer
    user = CustomUser.objects.create_user(
        username='developer', email='developer@example.com', password='password123'
    )
    authenticate_client(client, user)

    # Create necessary data for the session
    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    user.stack = stack
    user.level = level
    user.prog_language.add(prog_language)
    user.save()

    # Create a session that matches the user's skills
    project = Project.objects.create(
        owner=user,
        name='Test Project',
        stack=stack,
        level=level)
    project.languages.add(prog_language)

    session = Session.objects.create(
        project=project,
        host=user,
        description='Test Session',
        stack=stack,
        level=level,
        schedule_date_time=datetime.now())
    session.languages.add(prog_language)

    # When: I request suggested sessions
    url = reverse('suggested_sessions')
    response = client.get(url)

    # Then: I should receive a list of suggested sessions
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_session_serializer_language_validation_error(client):
    """
    Scenario: Validation error when creating a session with an invalid language
    Given I am creating a session
    When I include a language that is not part of the project
    Then I should receive a validation error
    """
    # Given: I am an authenticated user creating a session
    user = CustomUser.objects.create_user(
        username='testuser', email='testuser@example.com', password='password123'
    )
    authenticate_client(client, user)

    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')
    other_language, _ = ProgLanguage.objects.get_or_create(name='Java')

    project = Project.objects.create(owner=user, name='Test Project', stack=stack, level=level)
    project.languages.add(prog_language)  # Project only supports 'Python'

    # When: I include a language that is not part of the project
    url = '/api/projects/sessions/'
    data = {
        'name': 'Test Session',
        'description': 'Test Session',
        'schedule_date_time': '2024-01-01T12:00:00Z',
        'duration': 7200,
        'stack_id': stack.id,
        'level_id': level.id,
        'language_ids': [other_language.id]  # Invalid language 'Java'
    }
    response = client.post(url, data)

    # Then: I should receive a validation error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'languages' in response.data


@pytest.mark.django_db
def test_project_serializer_validation_error():
    """
    Scenario: Project creation fails due to missing required fields
    Given I am a logged-in user
    When I try to create a project without required fields
    Then I should receive validation errors
    """
    serializer_data = {
        'name': '',  # Missing required field
        'stack': 1,
        'languages': [1],
        'level': 1,
    }
    serializer = ProjectSerializer(data=serializer_data)

    # Then: Serializer should be invalid due to missing required fields
    assert not serializer.is_valid()
    assert 'name' in serializer.errors
