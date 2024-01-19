from django.urls import path

from ksatria_muslim.invoice import views

app_name = 'invoice'

urlpatterns = [
    path("test/", views.invoice_test, name="invoice-test"),
    path("webhook-test/", views.webhook_test, name="webhook-test"),
    path("webhook/", views.webhook, name="webhook"),
    path("simple-list/", views.simple_list_non_locked_time_entries, name="simple-list"),
]
