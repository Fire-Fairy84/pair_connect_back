import pytest
from django.core import mail


@pytest.fixture(autouse=True)
def disable_email_backend_for_tests(settings):
    # Disable email sending during tests
    settings.DJOSER['SEND_ACTIVATION_EMAIL'] = False
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
