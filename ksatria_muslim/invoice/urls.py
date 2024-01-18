from django.urls import path

from ksatria_muslim.invoice import views

app_name = 'invoice'

urlpatterns = [
    path("test/", views.invoice_test, name="invoice-test"),
    path("webhook-test/", views.webhook_test, name="webhook-test"),
    path("webhook/", views.webhook, name="webhook"),
]
