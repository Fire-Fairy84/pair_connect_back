import pytest
from rest_framework import status
from templated_mail import mail
from django.core import mail
import json
from projects.serializers import ProjectSerializer
from users.models import CustomUser
from projects.models import Project, Session, InterestedParticipant
from skills.models import Stack, Level, ProgLanguage
from datetime import datetime, timedelta
from django.urls import reverse
from datetime import timedelta


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

    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    user.stack = stack
    user.level = level
    user.prog_language.add(prog_language)
    user.save()

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
def test_session_serializer_language_valid(client):
    """
    Scenario: Session creation succeeds when the provided language is part of the project
    Given I am creating a session
    When I include a language that is part of the project
    Then the session should be created successfully
    """
    # Given: I am an authenticated user creating a session
    user = CustomUser.objects.create_user(
        username='testuser', email='testuser@example.com', password='password123'
    )
    authenticate_client(client, user)

    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    project = Project.objects.create(owner=user, name='Test Project', stack=stack, level=level)
    project.languages.add(prog_language)

    # When: I include a language that is part of the project
    url = '/api/projects/sessions/'
    data = {
        'project': project.id,
        'name': 'Test Session',
        'description': 'Test Session',
        'schedule_date_time': '2024-01-01T12:00:00Z',
        'duration': 7200,
        'stack_id': stack.id,
        'level': level.id,
        'languages': [prog_language.id]
    }
    response = client.post(url, data)

    # Then: The session should be created successfully
    assert response.status_code == status.HTTP_201_CREATED
    assert 'id' in response.data


@pytest.mark.django_db
def test_project_serializer_validation_error():
    """
    Scenario: Project creation fails due to missing required fields
    Given I am a logged-in user
    When I try to create a project without required fields
    Then I should receive validation errors
    """
    # Given: I am a logged-in user

    # When: I try to create a project without required fields
    serializer_data = {
        'name': '',
        'stack': 1,
        'languages': [1],
        'level': 1,
    }
    serializer = ProjectSerializer(data=serializer_data)

    # Then: Serializer should be invalid due to missing required fields
    assert not serializer.is_valid()
    assert 'name' in serializer.errors


@pytest.mark.django_db
def test_session_creation_with_invalid_project_id(client):
    """
    Scenario: Creating a session with a non-existent project ID should fail
    Given I am an authenticated user
    When I try to create a session with an invalid project ID
    Then I should receive a validation error
    """
    # Given: I am an authenticated user
    user = CustomUser.objects.create_user(
        username='testuser', email='testuser@example.com', password='password123'
    )
    authenticate_client(client, user)

    # When: I try to create a session with an invalid project ID
    url = '/api/projects/sessions/'
    data = {
        'project': 999,
        'name': 'Invalid Project Session',
        'description': 'This session should fail due to invalid project ID.',
        'schedule_date_time': '2024-01-01T12:00:00Z',
        'duration': 7200,
        'stack_id': 1,
        'level': 1,
        'languages': [1]
    }
    response = client.post(url, data)

    # Then: I should receive a validation error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Project does not exist.' in str(response.data)


@pytest.mark.django_db
def test_session_creation_missing_required_fields(client):
    """
    Scenario: Creating a session without required fields should fail
    Given I am an authenticated user
    When I try to create a session without required fields
    Then I should receive validation errors
    """
    # Given: I am an authenticated user
    user = CustomUser.objects.create_user(
        username='testuser', email='testuser@example.com', password='password123'
    )
    authenticate_client(client, user)

    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    project = Project.objects.create(owner=user, name='Test Project', stack=stack, level=level)
    project.languages.add(prog_language)

    # When: I try to create a session without required fields
    url = '/api/projects/sessions/'
    data = {
        'project': project.id,
        'description': 'Session without required fields.',
        'duration': 7200,
        'stack_id': stack.id,
        'level': level.id,
        'languages': [prog_language.id]
    }
    response = client.post(url, data)

    # Then: I should receive validation errors
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'name' in response.data
    assert 'schedule_date_time' in response.data


@pytest.mark.django_db
def test_session_update_by_non_host(client):
    """
    Scenario: Non-host user attempts to update a session should fail
    Given a session exists
    And I am authenticated as a different user
    When I try to update the session
    Then I should receive a permission error
    """
    # Given: a session exists, and I am authenticated as a different user
    host = CustomUser.objects.create_user(
        username='host', email='host@example.com', password='password123'
    )
    other_user = CustomUser.objects.create_user(
        username='otheruser', email='other@example.com', password='password123'
    )

    authenticate_client(client, host)

    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    project = Project.objects.create(owner=host, name='Host Project', stack=stack, level=level)
    project.languages.add(prog_language)

    # When: Creating a session with the correct duration type (timedelta)
    session = Session.objects.create(
        project=project,
        host=host,
        name='Host Session',
        description='Session by host.',
        schedule_date_time='2024-01-01T12:00:00Z',
        duration=timedelta(hours=2),
        stack=stack,
        level=level
    )

    authenticate_client(client, other_user)

    url = f'/api/projects/sessions/{session.id}/'
    data = {
        'name': 'Updated Session by Non-Host',
        'description': 'Non-host attempting to update session.',
        'schedule_date_time': '2024-01-01T15:00:00Z',
        'duration': 10800,
        'stack_id': stack.id,
        'level_id': level.id,
        'language_ids': [prog_language.id],
    }

    response = client.put(url, data=json.dumps(data), content_type='application/json')

    # Then: Non-host user should receive a permission error
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_session_deletion_by_host(client):
    """
    Scenario: Host user deletes a session successfully
    Given a session exists
    And I am authenticated as the host
    When I delete the session
    Then the session should be deleted successfully
    """
    # Given: a session exists
    host = CustomUser.objects.create_user(
        username='host', email='host@example.com', password='password123'
    )

    # And I am authenticated as the host
    authenticate_client(client, host)

    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    project = Project.objects.create(owner=host, name='Host Project', stack=stack, level=level)
    project.languages.add(prog_language)

    session = Session.objects.create(
        project=project,
        host=host,
        name='Host Session',
        description='Session to be deleted.',
        schedule_date_time='2024-01-01T12:00:00Z',
        duration=timedelta(hours=2),
        stack=stack,
        level=level
    )
    session.languages.add(prog_language)

    # When: I delete the session
    url = f'/api/projects/sessions/{session.id}/'
    response = client.delete(url)

    # Then: the session should be deleted successfully
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Session.objects.filter(id=session.id).exists()


@pytest.mark.django_db
def test_confirm_participant_success(client):
    """
    Scenario: Host confirms a participant successfully
    Given I am the host of a session
    And a developer is interested in the session
    When I confirm the developer as a participant
    Then the developer should be added as a participant and receive a confirmation email
    """
    # Given: I am the host of a session
    host = CustomUser.objects.create_user(
        username='host', email='host@example.com', password='password123'
    )
    developer = CustomUser.objects.create_user(
        username='developer', email='developer@example.com', password='password123'
    )
    authenticate_client(client, host)

    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    project = Project.objects.create(owner=host, name='Host Project', stack=stack, level=level)
    project.languages.add(prog_language)

    session = Session.objects.create(
        project=project,
        host=host,
        name='Host Session',
        description='Session for confirming participant.',
        schedule_date_time='2024-01-01T12:00:00Z',
        duration=timedelta(seconds=7200),
        stack=stack,
        level=level
    )
    session.languages.add(prog_language)

    InterestedParticipant.objects.create(user=developer, session=session)

    # When: I confirm the developer as a participant
    url = f'/api/projects/sessions/{session.id}/confirm-participant/'
    data = {'username': developer.username}
    response = client.post(url, data)

    # Then: The developer should be added as a participant and receive a confirmation email
    assert response.status_code == status.HTTP_200_OK
    assert 'confirmed' in response.data['message'].lower()
    assert session.participants.filter(id=developer.id).exists()
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert developer.email in email.to
    assert 'confirmadx' in email.subject.lower()


@pytest.mark.django_db
def test_confirm_participant_by_non_host(client):
    """
    Scenario: Non-host user attempts to confirm a participant should fail
    Given a session exists
    And I am authenticated as a different user
    When I try to confirm a participant
    Then I should receive a permission error
    """
    # Given: A session exists and I am authenticated as a different user
    host = CustomUser.objects.create_user(
        username='host', email='host@example.com', password='password123'
    )
    non_host = CustomUser.objects.create_user(
        username='nonhost', email='nonhost@example.com', password='password123'
    )
    developer = CustomUser.objects.create_user(
        username='developer', email='developer@example.com', password='password123'
    )
    authenticate_client(client, non_host)

    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    project = Project.objects.create(owner=host, name='Host Project', stack=stack, level=level)
    project.languages.add(prog_language)

    session = Session.objects.create(
        project=project,
        host=host,
        name='Host Session',
        description='Session to confirm participant.',
        schedule_date_time='2024-01-01T12:00:00Z',
        duration=timedelta(seconds=7200),
        stack=stack,
        level=level
    )
    session.languages.add(prog_language)

    InterestedParticipant.objects.create(user=developer, session=session)

    # When: I try to confirm a participant as a non-host user
    url = f'/api/projects/sessions/{session.id}/confirm-participant/'
    data = {'username': developer.username}
    response = client.post(url, data)

    # Then: I should receive a permission error
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'only the host can confirm participants.' in response.data['error'].lower()
    assert not session.participants.filter(id=developer.id).exists()


@pytest.mark.django_db
def test_express_interest_in_session(client):
    """
    Scenario: User expresses interest in a session successfully
    Given a session exists
    And I am an authenticated user
    When I express interest in the session
    Then I should receive a success message and an interest notification email should be sent
    """
    # Given: A session exists and I am an authenticated user
    host = CustomUser.objects.create_user(
        username='host', email='host@example.com', password='password123'
    )
    developer = CustomUser.objects.create_user(
        username='developer', email='developer@example.com', password='password123'
    )
    authenticate_client(client, developer)

    stack, _ = Stack.objects.get_or_create(name='Backend')
    level, _ = Level.objects.get_or_create(name='Junior')
    prog_language, _ = ProgLanguage.objects.get_or_create(name='Python')

    project = Project.objects.create(owner=host, name='Host Project', stack=stack, level=level)
    project.languages.add(prog_language)

    session = Session.objects.create(
        project=project,
        host=host,
        name='Host Session',
        description='Session for expressing interest.',
        schedule_date_time='2024-01-01T12:00:00Z',
        duration=timedelta(seconds=7200),
        stack=stack,
        level=level
    )
    session.languages.add(prog_language)

    # When: I express interest in the session
    url = '/api/projects/interested-participants/'
    data = {'session': session.id}
    response = client.post(url, data)

    # Then: I should receive a success message and an interest notification email should be sent
    assert response.status_code == status.HTTP_201_CREATED
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert host.email in email.to
    assert 'interesadx' in email.subject.lower()



