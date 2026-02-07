from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from manager.models import (
    Position,
    TaskType,
    Tag,
    Worker,
    Team,
    Project,
    Task,
)

admin.site.register(Position)
admin.site.register(TaskType)
admin.site.register(Tag)
admin.site.register(Team)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "task_type",
        "deadline",
        "priority",
        "completed",
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "completed"]
    filter_horizontal = ["teams"]


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("position",)


admin.site.unregister(Group)
