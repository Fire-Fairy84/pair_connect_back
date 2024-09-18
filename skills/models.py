from django.db import models


class Stack(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Level(models.Model):
    name = models.CharField(max_length=50)  # E.g., 'Junior', 'Mid', 'Senior'

    def __str__(self):
        return self.name


class ProgLanguage(models.Model):
    name = models.CharField(max_length=100)  # E.g., 'Python', 'JavaScript'

    def __str__(self):
        return self.name
