from django.utils import timezone

from config.celery_app import app
from ksatria_muslim.children_task.models import Task, TaskHistory


@app.task
def generate_children_tasks():
    """Should be generated for today"""
    today = timezone.localtime()
    base_tasks = Task.objects.filter(
        days__contains=[today.isoweekday()],
        active=True,
    )

    histories = []
    for task in base_tasks:
        for child in task.children.all():
            history = TaskHistory(
                task=task,
                child=child,
            )
            histories.append(history)

    TaskHistory.objects.bulk_create(histories)


