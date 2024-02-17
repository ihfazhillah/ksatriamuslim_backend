from django.utils import timezone

from ksatria_muslim.children_task.models import Task, TaskHistory


def get_children_tasks(child_id) -> list[TaskHistory]:
    tasks = Task.objects.filter(children__id=child_id)
    today = timezone.now().today()
    today_histories = [
        TaskHistory.objects.get_or_create(created__date=today, task_id=task.id, child_id=child_id)
        for task in tasks
    ]
    today_histories = sorted(today_histories, key=lambda history: history.modified, reverse=True)
    return [instance for instance, created in today_histories]
