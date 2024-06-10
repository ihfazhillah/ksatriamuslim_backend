from django.urls import path

from ksatria_muslim.children_task import views

app_name = "children_task"

urlpatterns = [
    # child URLS
    path("children/", views.get_children, name="get-children"),
    path("children/<child_id>/tasks/", views.get_task_list, name="get-task-list"),
    path("mark-as-finished/", views.mark_as_finished, name="mark-as-finished"),
    path("mark-as-udzur/", views.mark_as_udzur, name="mark-as-udzur"),

    # parent URLS
    path("dashboard/today/", views.today_parent_dashboard, name="today-parent-dashboard"),
    path("to-review-tasks/", views.to_review_tasks_view, name="to-review-tasks"),
    path("update-status/", views.update_status, name="update-status"),
    path("confirm/", views.confirm, name="confirm"),
    path("reset/", views.reset, name="reset"),
    # todo:
    # - list task global per parent
    # - create task
    # - update task
]
