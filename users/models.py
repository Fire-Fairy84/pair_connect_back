from django.db import models
from django.contrib.auth.models import AbstractUser
from skills.models import Stack, Level, ProgLanguage


class CustomUser(AbstractUser):
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    stack = models.ForeignKey(Stack, on_delete=models.SET_NULL, null=True, blank=True)
    prog_language = models.ForeignKey(ProgLanguage, on_delete=models.SET_NULL, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    about_me = models.TextField(null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    linkedin_link = models.URLField(max_length=255, null=True, blank=True)
    github_link = models.URLField(max_length=255, null=True, blank=True)
    discord_link = models.URLField(max_length=255, null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'name']

    def __str__(self):
        return f"{self.username} {self.email}"
