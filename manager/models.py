from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from manager_service import settings


class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TaskType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name="workers",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Worker"

    def __str__(self):
        return f"{self.username} {self.position or ''}"


class Team(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="teams"
    )

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    completed = models.BooleanField(default=False)
    teams = models.ManyToManyField(
        Team,
        related_name="projects",
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("manager:project-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


TASK_PRIORITIES = (
    ("LOW", "Low"),
    ("MEDIUM", "Medium"),
    ("HIGH", "High"),
    ("VERY HIGH", "Very High"),
    ("URGENT", "Urgent"),
)


class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True, null=True)
    deadline = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    priority = models.TextField(
        choices=TASK_PRIORITIES,
        default=TASK_PRIORITIES[0],
        blank=True, null=True
    )

    task_type = models.ForeignKey(
        TaskType, on_delete=models.CASCADE, related_name="tasks"
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="tasks"
    )
    tags = models.ManyToManyField(Tag, related_name="tasks", blank=True)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    def get_absolute_url(self):
        return reverse("manager:task-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.name} ({self.priority})"
