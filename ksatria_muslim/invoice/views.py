import datetime
import decimal
import json
from functools import reduce

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.templatetags import static
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML, CSS
from weasyprint.css import find_stylesheets
from weasyprint.text.fonts import FontConfiguration

from ksatria_muslim.invoice.domain.data import Invoice, Company, Client, LineItem, Unit, Currency
from ksatria_muslim.invoice.integrations.clockify import parse_time_entry
from ksatria_muslim.invoice.integrations.converters import Clockify
from ksatria_muslim.invoice.models import WebhookTest, ClockifyWebhookIntegration, ClockifyIntegration, TimeEntry, \
    Project


def invoice_test(request):
    line_items = [
        LineItem("New Year Gift", 1, Unit.PCS, 100, 100),
        LineItem("Candid Clara", 9.75, Unit.HOURLY, 25, 243.75)
    ]
    invoice = Invoice(
        company=Company("Muhammad Ihfazhillah", "me@ihfazh.com"),
        client=Client("Jonathan Leanne", "jon@test.com"),
        number="#INV0001",
        date=datetime.date.today(),
        line_items=line_items,
        total=564.75,
        currency=Currency("$", "USD")
    )


    font_config = FontConfiguration()
    html_string = render_to_string("invoice/test-invoice.html", {"invoice": invoice})

    html = HTML(string=html_string, base_url=request.build_absolute_uri())

    html.write_pdf("invoice.pdf", font_config=font_config, pagesize="a4")
    return render(request, "invoice/test-invoice.html", {"invoice": invoice})


@csrf_exempt
def webhook_test(request: HttpRequest):
    headers = request.headers
    body = request.body
    post = request.POST

    WebhookTest.objects.create(headers=headers, body=body, post=post)
    return JsonResponse({"success": True})

@csrf_exempt
def webhook(request: HttpRequest):
    headers = request.headers

    body_string = request.body.decode()
    body = json.loads(body_string)

    clockify_key = headers.get("Clockify-Signature")
    if not clockify_key:
        return JsonResponse({"message": "no clockify key"}, status=401)

    clockify_event_key = headers.get("Clockify-Webhook-Event-Type")
    if not clockify_event_key:
        return JsonResponse({"message": "no clockify event key"}, status=401)

    webhook_integration = ClockifyWebhookIntegration.objects.filter(
        key=clockify_key,
        event_key=clockify_event_key
    ).first()

    if not webhook_integration:
        return JsonResponse({"message": "clockify webhook not registered"}, status=401)

    entry = parse_time_entry(body)
    integration = ClockifyIntegration.objects.filter(
        integrated_project__user=webhook_integration.user,
        project_id=entry.project_id
    ).first()
    if not integration:
        # just pass
        return JsonResponse({"message": "cannot find integration"}, status=200)

    converter = Clockify(integration)

    time_entry = converter.time_entry_to_django(entry)

    instance = TimeEntry.objects.filter(
        ref_id=time_entry.ref_id,
        ref_name=time_entry.ref_name
    ).first()

    if clockify_event_key in ["TIMER_STOPPED", "TIME_ENTRY_UPDATED"]:
        if not instance:
            time_entry.save()
        else:
            time_entry.id = instance.id
            time_entry.save(force_update=True)

    if clockify_event_key == "TIME_ENTRY_DELETED":
        if instance:
            time_entry.id = instance.id
            time_entry.delete()

    if clockify_event_key == "NEW_TIME_ENTRY":
        time_entry.save()

    return JsonResponse({"success": True})


@login_required
def simple_list_non_locked_time_entries(request):
    """
    Tujuannya untuk nampilkan sementara
    """
    projects = Project.objects.all()
    data = []

    for project in projects:
        entries = project.timeentry_set.filter(locked=False)
        total_duration = reduce(lambda acc, entry: acc + entry.duration, entries, datetime.timedelta())
        total_hours = total_duration.total_seconds() / 3600
        data.append({
            "description": project.name,
            "rate": project.rate,
            "qty": total_hours,
            "total": decimal.Decimal(total_hours) * project.rate
        })

    total_usd = reduce(lambda acc, item: acc + item["total"], data, 0)

    try:
        url = f"https://api.freecurrencyapi.com/v1/latest?apikey={settings.FREE_CURRENCY_API_KEY}&currencies=IDR"
        response = requests.get(url)
        response_data = response.json()
        currency = response_data["data"]["IDR"]
    except Exception:
        currency = 1

    total_idr = decimal.Decimal(currency) * total_usd

    return render(request, "invoice/simple_non_locked.html", {
        "data": data,
        "total_usd": total_usd,
        "total_idr": total_idr,
        "currency": currency
    })

