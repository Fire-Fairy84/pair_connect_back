"""
Feature: User Registration

  As a new user,
  I want to register an account,
  So that I can access and use the application's features.

  Scenario: Successful user registration
    Given I am a new user
    When I register with valid data:
      | field        | value                         |
      | username     | test_user                     |
      | email        | email@example.com             |
      | name         | John Doe                      |
      | password     | Password123!                  |
      | password2    | Password123!                  |
    Then I should receive a confirmation that my account has been created
    And I should be able to log in with my username and password

  Scenario: Registration fails due to non-matching passwords
    Given I am a new user
    When I register with passwords that do not match:
      | field        | value                         |
      | username     | test_user                     |
      | email        | email@example.com             |
      | name         | John Doe                      |
      | password     | Password123!                  |
      | password2    | DifferentPassword123!         |
    Then I should receive an error message stating that the passwords do not match

  Scenario: Registration fails due to missing required fields
    Given I am a new user
    When I register without providing all required fields:
      | field     | value |
      | username  |       |
      | email     |       |
      | name      |       |
      | password  |       |
      | password2 |       |
    Then I should receive error messages indicating the missing fields

  Scenario: Registration fails due to existing username
    Given a user with username "test_user" already exists
    When I register with username "test_user":
      | field        | value                         |
      | username     | test_user                     |
      | email        | newemail@example.com          |
      | name         | Jane Doe                      |
      | password     | Password123!                  |
      | password2    | Password123!                  |
    Then I should receive an error message stating that the username is already in use

  Scenario: Registration fails due to existing email
    Given a user with email "email@example.com" already exists
    When I register with email "email@example.com":
      | field        | value                         |
      | username     | new_user                      |
      | email        | email@example.com             |
      | name         | Jane Doe                      |
      | password     | Password123!                  |
      | password2    | Password123!                  |
    Then I should receive an error message stating that the email is already in use

  Scenario: Successful registration with optional fields
    Given I am a new user
    When I register with valid data and optional fields:
      | field           | value                                   |
      | username        | test_user                               |
      | email           | email@example.com                       |
      | name            | John Doe                                |
      | password        | Password123!                            |
      | password2       | Password123!                            |
      | about_me        | I am a passionate developer.            |
      | telephone       | 123456789                               |
      | linkedin_link   | https://www.linkedin.com/in/testuser/   |
      | github_link     | https://github.com/testuser             |
      | discord_link    | testuser#1234                           |
    Then I should receive a confirmation that my account has been created
    And my profile should include the provided optional information
"""

# tests/test_user_registration.py

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser

# Path to the feature file
scenarios('features/user_registration.feature')


@pytest.fixture
def api_client():
    return APIClient()


@given('I am a new user')
def new_user():
    # Ensure the database is clean
    CustomUser.objects.all().delete()


@given(parsers.parse('a user with username "{username}" already exists'))
def existing_user_with_username(username):
    CustomUser.objects.create_user(
        username=username,
        email='existingemail@example.com',
        password='ExistingPassword123!'
    )


@given(parsers.parse('a user with email "{email}" already exists'))
def existing_user_with_email(email):
    CustomUser.objects.create_user(
        username='existing_user',
        email=email,
        password='ExistingPassword123!'
    )


@when(parsers.parse('I register with valid data:\n{data}'))
def register_with_valid_data(api_client, data):
    payload = parse_table(data)
    api_client.response = api_client.post(reverse('user-register'), payload, format='multipart')


@when(parsers.parse('I register with passwords that do not match:\n{data}'))
def register_with_password_mismatch(api_client, data):
    payload = parse_table(data)
    api_client.response = api_client.post(reverse('user-register'), payload, format='multipart')


@when(parsers.parse('I register without providing all required fields:\n{data}'))
def register_with_missing_fields(api_client, data):
    payload = parse_table(data)
    api_client.response = api_client.post(reverse('user-register'), payload, format='multipart')


@when(parsers.parse('I register with username "{username}":\n{data}'))
def register_with_existing_username(api_client, username, data):
    payload = parse_table(data)
    payload['username'] = username
    api_client.response = api_client.post(reverse('user-register'), payload, format='multipart')


@when(parsers.parse('I register with email "{email}":\n{data}'))
def register_with_existing_email(api_client, email, data):
    payload = parse_table(data)
    payload['email'] = email
    api_client.response = api_client.post(reverse('user-register'), payload, format='multipart')


@when(parsers.parse('I register with valid data and optional fields:\n{data}'))
def register_with_optional_fields(api_client, data):
    payload = parse_table(data)
    api_client.response = api_client.post(reverse('user-register'), payload, format='multipart')


@then('I should receive a confirmation that my account has been created')
def confirm_account_creation(api_client):
    assert api_client.response.status_code == status.HTTP_201_CREATED


@then('I should be able to log in with my username and password')
def login_with_new_credentials(api_client):
    payload = {
        'username': api_client.response.data['username'],
        'password': 'Password123!'  # Ensure this matches the test password
    }
    response = api_client.post(reverse('login'), payload, format='json')
    assert response.status_code == status.HTTP_200_OK


@then('I should receive an error message stating that the passwords do not match')
def passwords_do_not_match_error(api_client):
    assert api_client.response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password' in api_client.response.data


@then('I should receive error messages indicating the missing fields')
def missing_fields_error(api_client):
    assert api_client.response.status_code == status.HTTP_400_BAD_REQUEST
    required_fields = ['username', 'email', 'name', 'password', 'password2']
    for field in required_fields:
        assert field in api_client.response.data


@then('I should receive an error message stating that the username is already in use')
def username_in_use_error(api_client):
    assert api_client.response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in api_client.response.data


@then('I should receive an error message stating that the email is already in use')
def email_in_use_error(api_client):
    assert api_client.response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in api_client.response.data


@then('my profile should include the provided optional information')
def profile_includes_optional_info(api_client):
    user = CustomUser.objects.get(username=api_client.response.data['username'])
    optional_fields = ['about_me', 'telephone', 'linkedin_link', 'github_link', 'discord_link']
    for field in optional_fields:
        assert getattr(user, field) == api_client.response.data.get(field)


# Helper function to parse the table data
def parse_table(data):
    lines = data.strip().split('\n')
    headers = [header.strip() for header in lines[0].strip('|').split('|')]
    values = [value.strip() for value in lines[1].strip('|').split('|')]
    return dict(zip(headers, values))
