from rest_framework import serializers

from .models import Task, User


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "status", "created_at", "updated_at"]


class EmployeeWorkloadSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(
        many=True, read_only=True, source="tasks"
    )  # Задачи, связанные с сотрудником

    class Meta:
        model = User
        fields = ["id", "username", "email", "tasks"]
