import pytest
from django.core import mail


@pytest.fixture(autouse=True)
def enable_mail_testing(settings):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    mail.outbox = []
