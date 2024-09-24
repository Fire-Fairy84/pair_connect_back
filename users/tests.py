import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser


REGISTER_URL = '/api/auth/users/'

@pytest.mark.django_db
def test_user_registration_success(client):
    """
    Scenario: Successful user registration
    Given I am a new user
    When I register with valid required data:
    Then I should receive a confirmation that my account has been created
    """
    data = {
        'username': 'harrypotter',
        'email': 'harrypotter@email.com',
        'name': 'Harry Potter',
        'password': 'mypassword123',
        're_password': 'mypassword123',  # Djoser requires both password and re_password
    }
    response = client.post(REGISTER_URL, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.filter(username='harrypotter').exists()


@pytest.mark.django_db
def test_user_registration_password_does_not_match(client):
    """
    Scenario: Registration fails due to non-matching passwords
    Given I am a new user
    When I register with passwords that do not match:
    Then I should receive an error message stating that the passwords do not match
    """
    url = reverse('user-register')
    data = {
        'username': 'ronweasley',
        'email': 'ron@email.com',
        'name': 'Rone Weasley',
        'password': 'mypassword123',
        'password2': 'notmypassword123',
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password' in response.data
    assert not CustomUser.objects.filter(username='ronweasley').exists()


@pytest.mark.django_db
def test_user_registration_missing_fields(client):
    """
    Scenario: Registration fails due to missing required fields
    Given I am a new user
    When I register without providing all required fields:
    Then I should receive error messages indicating the missing fields
    """
    url = reverse('user-register')
    data = {
        'username': 'dumbledore',
        # 'email' is missing
        'name': 'Albus Dumbledore',
        'password': 'mypassword123',
        'password2': 'mypassword123',
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data
    assert not CustomUser.objects.filter(username='johndoe').exists()


@pytest.mark.django_db
def test_user_registration_duplicate_username(client):
    """
    Scenario: Registration fails due to existing username
    Given a user with username "voldemort" already exists
    When I register with username "voldemort":
    Then I should receive an error message stating that the username is already in use
    """
    CustomUser.objects.create_user(
        username='voldemort',
        email='tomriddle@email.com',
        password='mypassword123',
        name='Tom Riddle'
    )
    url = reverse('user-register')
    data = {
        'username': 'voldemort',
        'email': 'noname@email.com',
        'name': 'Marvolo',
        'password': 'password789',
        'password2': 'password789',
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data
    assert CustomUser.objects.filter(email='noname@email.com').count() == 0


@pytest.mark.django_db
def test_user_registration_duplicate_email(client):
    """
    Scenario: Registration fails due to existing email
    Given a user with email "hagrid@email.com" already exists
    When I register with email "hagrid@email.com":
    Then I should receive an error message stating that the email is already in use
    """
    CustomUser.objects.create_user(
        username='hagrid',
        email='hagrid@email.com',
        password='mypassword123',
        name='Hagrid'
    )
    url = reverse('user-register')
    data = {
        'username': 'realhagrid',
        'email': 'hagrid@email.com',
        'name': 'Rubeus Hagrid',
        'password': 'password321',
        'password2': 'password321',
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data
    assert CustomUser.objects.filter(username='realhagrid').count() == 0
