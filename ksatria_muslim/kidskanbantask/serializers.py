from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    completed = serializers.BooleanField()
    childId = serializers.CharField(read_only=True)
    imageUrl = serializers.URLField(read_only=True)

class ChildWithTasksSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

class BoardStateSerializer(serializers.Serializer):
    children = ChildWithTasksSerializer(many=True, read_only=True)
