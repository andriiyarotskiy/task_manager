from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from manager.models import Worker, Team, Task, Tag


class WorkerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "username", "first_name", "last_name", "position",
        )


class TeamForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        required=False,
        queryset=get_user_model().objects.select_related("position"),
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = Team
        fields = "__all__"


class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        required=False,
        queryset=get_user_model().objects.select_related("position"),
        widget=forms.CheckboxSelectMultiple(

        ),
    )

    class Meta:
        model = Task
        fields = (
            "name",
            "completed",
            "task_type",
            "project",
            "deadline",
            "priority",
            "description",
            "assignees"
        )
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter task description...'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }
