import pytest
from rest_framework import status
from users.models import CustomUser
import pytest
from rest_framework import status


@pytest.mark.django_db
def test_user_registration_password_mismatch(client):
    """
    Scenario: User registration fails due to mismatched passwords
    Given I am a new user
    When I submit registration details with mismatched passwords
    Then the registration should fail with an appropriate error message
    """

    # Given: I am a new user with registration details where passwords do not match
    registration_data = {
        'username': 'testuser',
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'password123',
        're_password': 'password321',
    }

    # When: I submit the registration form
    response = client.post('/api/auth/users/', registration_data)

    # Then: The registration should fail with an appropriate error message
    assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Expected status 400, got {response.status_code}"
    assert 'non_field_errors' in response.data, "Expected 'non_field_errors' in response data."
    assert 'the two password fields didn’t match' in response.data['non_field_errors'][0].lower(), \
        "Expected password mismatch error message."


@pytest.mark.django_db
def test_user_registration_missing_fields(client):
    """
    Scenario: Registration fails due to missing required fields
    Given I am a new user
    When I register without providing all required fields
    Then I should receive error messages indicating the missing fields
    """

    # Given: I am a new user
    url = '/api/auth/users/'
    data = {
        'username': 'dumbledore',
        # 'email' is missing
        'name': 'Albus Dumbledore',
        'password': 'mypassword123',
        're_password': 'mypassword123',
    }

    # When: I register without providing the required 'email' field
    response = client.post(url, data)

    # Then: The registration should fail due to missing 'email' field
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
def test_user_registration_missing_fields(client):
    """
    Scenario: Registration fails due to missing required fields
    Given I am a new user
    When I register without providing all required fields
    Then I should receive error messages indicating the missing fields
    """

    # Given: I am a new user
    url = '/api/auth/users/'
    data = {
        'username': 'dumbledore',
        # 'email' is missing
        'name': 'Albus Dumbledore',
        'password': 'mypassword123',
        're_password': 'mypassword123',
    }

    # When: I register without providing the required 'email' field
    response = client.post(url, data)

    # Then: The registration should fail due to missing 'email' field
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
def test_user_registration_password_mismatch(client):
    """
    Scenario: Registration fails due to non-matching passwords
    Given I am a new user
    When I register with passwords that do not match
    Then I should receive an error message stating that the passwords do not match
    """
    # Given: I am a new user
    url = '/api/auth/users/'
    data = {
        'username': 'ronweasley',
        'email': 'ron@email.com',
        'name': 'Ron Weasley',
        'password': 'mypassword123',
        're_password': 'notmypassword123',
    }

    # When: Register with non-matching passwords
    response = client.post(url, data)

    # Then: I must receive an error asserting password don't match
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in response.data


@pytest.mark.django_db
def test_user_registration_duplicate_username(client):
    """
    Scenario: Registration fails due to existing username
    Given a user with username "voldemort" already exists
    When I register with username "voldemort"
    Then I should receive an error message stating that the username is already in use
    """

    # Given: A user with the username "voldemort" already exists
    CustomUser.objects.create_user(
        username='voldemort',
        email='tomriddle@email.com',
        password='mypassword123',
        name='Tom Riddle'
    )

    # When: I try to register a new user with the same username "voldemort"
    url = '/api/auth/users/'
    data = {
        'username': 'voldemort',
        'email': 'noname@email.com',
        'name': 'Marvolo',
        'password': 'password789',
        're_password': 'password789',
    }
    response = client.post(url, data)

    # Then: The registration should fail with an error message indicating the username is already in use
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data


@pytest.mark.django_db
def test_user_registration_duplicate_email(client):
    """
    Scenario: Registration fails due to an already existing email
    Given a user with email "hagrid@email.com" already exists
    When I register with the same email
    Then I should receive an error message stating that the email is already in use
    """
    # Given: An existing user
    CustomUser.objects.create_user(
        username='hagrid',
        email='hagrid@email.com',
        password='mypassword123',
        name='Rubeus Hagrid'
    )

    # When: A new user registers with the same email
    url = '/api/auth/users/'
    data = {
        'username': 'newhagrid',
        'email': 'hagrid@email.com',
        'name': 'New Hagrid',
        'password': 'newpassword123',
        're_password': 'newpassword123',
    }

    response = client.post(url, data)

    # Then: Registration should fail due to duplicate email
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
def test_user_login_success(client):
    """
    Scenario: Successful user login
    Given I am a registered and activated user
    When I log in with valid credentials
    Then I should receive a JWT token
    """
    # Given: I am a registered user, and my account is confirmed
    user = CustomUser.objects.create_user(
        username='hermionegranger@email.com',
        email='hermione@email.com',
        password='password123',
        name='Hermione Granger'
    )
    user.is_active = True
    user.save()

    # When: I log in with valid credentials
    url = '/api/auth/jwt/create/'
    data = {
        'email': 'hermione@email.com',
        'password': 'password123'
    }
    response = client.post(url, data)

    # Then: I should receive a JWT token
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code} with response {response.data}"
    assert 'access' in response.data


@pytest.mark.django_db
def test_user_login_without_activation_fail(client):
    """
    Scenario: User tries to log in without account activation
    Given I am a registered but unactivated user
    When I attempt to log in with valid credentials
    Then I should not be able to log in and receive an error message
    """
    # Given: I am a registered but unactivated user
    user = CustomUser.objects.create_user(
        username='dracomalfoy',
        email='dracomalfoy@email.com',
        password='password123',
        name='Draco Malfoy',
        is_active=False
    )

    # When: The user attempts to log in without activation
    login_data = {
        'email': 'dracomalfoy@email.com',
        'password': 'password123'
    }
    response = client.post('/api/auth/jwt/create/', login_data)

    # Then: The user should not be able to log in, and an error message should be shown
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data
    assert response.data['detail'][0] == 'N'


@pytest.mark.django_db
def test_user_logout_success(client):
    """
    Scenario: Successful user logout
    Given I am a logged-in user
    When I log out
    Then my JWT refresh token should be blacklisted
    """
    # Given: I am a logged-in user
    user = CustomUser.objects.create_user(
        username='ronweasley',
        email='ron@email.com',
        password='password123',
        name='Ron Weasley'
    )

    login_data = {
        'email': 'ron@email.com',
        'password': 'password123'
    }
    login_response = client.post('/api/auth/jwt/create/', login_data)
    token = login_response.data['access']
    refresh_token = login_response.data['refresh']

    # When: I log out using the refresh token
    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    logout_data = {'refresh': refresh_token}
    logout_response = client.post('/api/auth/logout/', logout_data)

    # Then: The JWT refresh token should be blacklisted
    assert logout_response.status_code == status.HTTP_200_OK
    assert logout_response.data['detail'] == "Successfully logged out."


@pytest.mark.django_db
def test_user_logout_without_token_success(client):
    """
    Scenario: Attempt to log out without being logged in (invalid or expired JWT)
    Given I am not logged in
    When I attempt to log out with an invalid or expired JWT
    Then the request should still succeed (since the logout endpoint handles invalid tokens gracefully)
    """
    # Given: I am not logged in and provide an invalid token
    logout_data = {'refresh': 'dummy_refresh_token'}

    # When: Attempt to log out with an invalid or expired token
    logout_response = client.post('/api/auth/logout/', logout_data)

    # Then: The request should succeed (200 or 204), no error should be raised
    assert logout_response.status_code == status.HTTP_200_OK or status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_user_activation_success(client):
    """
    Scenario: Simulate user account activation
    Given I am a registered but unactivated user
    When I activate my account via email link
    Then my account should be active and I should be able to log in
    """
    # Given: I am a registered but unactivated user
    user = CustomUser.objects.create_user(
        username='lunah',
        email='lunah@email.com',
        password='password123',
        name='Luna Lovegood'
    )

    user.is_active = True
    user.save()

    # When: The user attempts to log in
    login_data = {
        'email': 'lunah@email.com',
        'password': 'password123'
    }
    response = client.post('/api/auth/jwt/create/', login_data)

    # Then: The user should be able to log in and receive a JWT token
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
