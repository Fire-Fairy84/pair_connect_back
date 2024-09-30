from datetime import timedelta
from cloudinary.models import CloudinaryField
from django.db import models
from skills.models import Stack, ProgLanguage, Level
from django.contrib.auth import get_user_model
from .services import SessionService, DeveloperSuggestionService

User = get_user_model()


class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = CloudinaryField('image', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    stack = models.ForeignKey(Stack, on_delete=models.CASCADE)
    languages = models.ManyToManyField(ProgLanguage)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    def image_url(self):
        if self.image:
            return self.image.url
        return None

    def __str__(self):
        return self.name


class Session(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sessions')
    host = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    schedule_date_time = models.DateTimeField()
    duration = models.DurationField(default=timedelta(hours=2))
    stack = models.ForeignKey(Stack, on_delete=models.SET_NULL, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    languages = models.ManyToManyField(ProgLanguage, blank=True)
    session_link = models.URLField(max_length=255, null=True, blank=True)
    participant_limit = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    public = models.BooleanField(default=True)
    participants = models.ManyToManyField(User, related_name='sessions_joined', blank=True)

    def save(self, *args, **kwargs):
        session_service = SessionService(self)
        session_service.inherit_level_from_project()
        session_service.validate_and_assign_stack()

        super(Session, self).save(*args, **kwargs)

    def suggest_developers(self):
        suggestion_service = DeveloperSuggestionService(self)
        return suggestion_service.get_suggested_developers()


class InterestedParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    date_created_interested = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} is interested in session {self.session.id}"
