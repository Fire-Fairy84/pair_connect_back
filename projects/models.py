from datetime import timedelta
from cloudinary.models import CloudinaryField
from django.db import models
from skills.models import Stack, ProgLanguage, Level
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = CloudinaryField('image', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    stack = models.ForeignKey(Stack, on_delete=models.SET_NULL, null=True, blank=True)
    languages = models.ManyToManyField(ProgLanguage, blank=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)

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
    prog_language = models.ForeignKey(ProgLanguage, on_delete=models.SET_NULL, null=True, blank=True)
    session_link = models.URLField(max_length=255, null=True, blank=True)
    participant_limit = models.IntegerField(default=0)  # 0 for unlimited participants
    active = models.BooleanField(default=True)
    public = models.BooleanField(default=True)
    participants = models.ManyToManyField(User, related_name='sessions_joined', blank=True)

    def save(self, *args, **kwargs):
        # Inherit stack: If the project stack is fullstack, require the user to specify frontend or backend
        if not self.stack:
            if self.project.stack.name == 'Fullstack':
                raise ValueError("Please specify whether the session is Frontend or Backend.")
            else:
                self.stack = self.project.stack
        if not self.level:
            self.level = self.project.level
        # Inherit programming language: If the project has multiple languages, require the user to specify one
        if not self.prog_language:
            if self.project.languages.count() > 1:
                raise ValueError("You must specify which programming language the session will use.")
            elif self.project.languages.count() == 1:
                self.prog_language = self.project.languages.first()

        super(Session, self).save(*args, **kwargs)


class InterestedParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    date_created_interested = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} is interested in session {self.session.id}"
