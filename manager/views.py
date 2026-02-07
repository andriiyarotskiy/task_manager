from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from manager.forms import WorkerCreationForm, TeamForm, TaskForm
from manager.mixin import CommonFormMixin
from manager.models import Project, Position, Team, Worker, TaskType, Task, Tag


@login_required
def index(request):
    context = {}
    if request.user.is_superuser:
        context["my_teams"] = Team.objects.all()
    else:
        context["my_teams"] = Team.objects.filter(members=request.user)

    context["incomplete_tasks"] = Task.objects.filter(Q(assignees=request.user) & Q(completed=False))

    return render(request, "manager/index.html", context=context)


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project

    def get_queryset(self):
        return Project.objects.prefetch_related(
            "teams",
            Prefetch(
                'tasks',
                queryset=Task.objects.filter(completed=True),
                to_attr='completed_tasks'
            ),
            Prefetch(
                'tasks',
                queryset=Task.objects.filter(completed=False),
                to_attr='incomplete_tasks',
            ),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.object)
        context["completed_tasks"] = self.object.completed_tasks
        context["incomplete_tasks"] = self.object.incomplete_tasks
        return context


class ProjectCreateView(
    LoginRequiredMixin,
    CommonFormMixin,
    generic.CreateView,
):
    model = Project
    success_url = reverse_lazy("manager:project-list")
    fields = ("name", "teams",)
    form_title = "Project"


class ProjectUpdateView(
    LoginRequiredMixin,
    CommonFormMixin,
    generic.UpdateView,
):
    model = Project
    success_url = reverse_lazy("manager:project-list")
    fields = ("name", "teams",)
    form_title = "Project"


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template_name = "common/confirm_delete.html"
    success_url = reverse_lazy("manager:project-list")


# Position

class PositionListView(LoginRequiredMixin, generic.ListView):
    model = Position


class PositionCreateView(LoginRequiredMixin, CommonFormMixin, generic.CreateView):
    model = Position
    form_title = "Position"
    success_url = reverse_lazy("manager:position-list")
    fields = "__all__"


class PositionUpdateView(LoginRequiredMixin, CommonFormMixin, generic.UpdateView):
    model = Position
    form_title = "Position"
    fields = "__all__"
    success_url = reverse_lazy("manager:position-list")


class PositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Position
    template_name = "common/confirm_delete.html"
    success_url = reverse_lazy("manager:position-list")


# Workers
class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()

    def get_queryset(self):
        queryset = Worker.objects.exclude(id=self.request.user.id)
        return queryset


class WorkerCreateView(LoginRequiredMixin, CommonFormMixin, generic.CreateView):
    model = get_user_model()
    form_title = "Worker Profile"
    success_url = reverse_lazy("manager:worker-list")
    form_class = WorkerCreationForm


class WorkerUpdateView(LoginRequiredMixin, CommonFormMixin, generic.UpdateView):
    model = get_user_model()
    form_title = "Worker Profile"
    form_class = WorkerCreationForm
    success_url = reverse_lazy("manager:worker-list")


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = get_user_model()
    template_name = "common/confirm_delete.html"
    success_url = reverse_lazy("manager:worker-list")


# Team
class TeamListView(LoginRequiredMixin, generic.ListView):
    model = Team

    def get_queryset(self):
        return Team.objects.prefetch_related(Prefetch(
            "members",
            queryset=get_user_model().objects.select_related("position"),
        ))


class TeamCreateView(LoginRequiredMixin, CommonFormMixin, generic.CreateView):
    model = Team
    form_class = TeamForm
    form_title = "Team"
    success_url = reverse_lazy("manager:team-list")


class TeamUpdateView(LoginRequiredMixin, CommonFormMixin, generic.UpdateView):
    model = Team
    form_class = TeamForm
    form_title = "Team"
    success_url = reverse_lazy("manager:team-list")


class TeamDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Team
    success_url = reverse_lazy("manager:team-list")
    template_name = "common/confirm_delete.html"


# Task Types
class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType
    template_name = "manager/task_type_list.html"
    context_object_name = "task_type_list"


class TaskTypeCreateView(LoginRequiredMixin, CommonFormMixin, generic.CreateView):
    model = TaskType
    fields = "__all__"
    form_title = "Task Type"
    success_url = reverse_lazy("manager:task-type-list")


class TaskTypeUpdateView(LoginRequiredMixin, CommonFormMixin, generic.UpdateView):
    model = TaskType
    fields = "__all__"
    form_title = "Task Type"
    success_url = reverse_lazy("manager:task-type-list")


class TaskTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = TaskType
    success_url = reverse_lazy("manager:task-type-list")
    template_name = "common/confirm_delete.html"


# TASK
class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task

    def get_queryset(self):
        queryset = (Task.objects
                    .select_related("project", "task_type")
                    .prefetch_related("tags"))
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(
            Q(assignees=self.request.user) | Q(assignees__isnull=True)
        )


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task


class TaskCreateView(LoginRequiredMixin, CommonFormMixin, generic.CreateView):
    model = Task
    form_title = "Task"
    form_class = TaskForm
    success_url = reverse_lazy("manager:task-list")


class TaskUpdateView(LoginRequiredMixin, CommonFormMixin, generic.UpdateView):
    model = Task
    form_title = "Task"
    form_class = TaskForm
    success_url = reverse_lazy("manager:task-list")


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = "common/confirm_delete.html"
    success_url = reverse_lazy("manager:task-list")


@login_required
def add_tag(request):
    task_id = request.POST.get("task_id")
    tag_name = request.POST.get("tag_name")
    if tag_name:
        task = get_object_or_404(Task, pk=task_id)
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        task.tags.add(tag)
    return redirect("manager:task-list")


@login_required
def edit_tag(request):
    tag_name = request.POST.get("tag_name")
    tag_id = request.POST.get("tag_id")
    if tag_name:
        tag = get_object_or_404(Tag, pk=tag_id)
        tag.name = tag_name
        tag.save()
    return redirect("manager:task-list")


@login_required
def delete_tag(request):
    task_id = request.POST.get("task_id")
    tag_id = request.POST.get("tag_id")
    task = get_object_or_404(Task, pk=task_id)
    if task.tags.filter(pk=tag_id).exists():
        task.tags.remove(tag_id)
    return redirect("manager:task-list")
