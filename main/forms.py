from django.forms import BooleanField, ModelForm

from main.models import Task, TaskComment


class StyleFormMixin(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class TaskForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Task
        fields = ("title", "description", "img", )


class ModeratorTaskForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Task
        fields = ("status", "commentary")


class CommentaryTaskForm(StyleFormMixin, ModelForm):
    class Meta:
        model = TaskComment
        fields = ("content",)
