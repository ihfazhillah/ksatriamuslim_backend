import datetime
import json

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.templatetags import static
from weasyprint import HTML, CSS
from weasyprint.css import find_stylesheets
from weasyprint.text.fonts import FontConfiguration

from ksatria_muslim.invoice.domain.data import Invoice, Company, Client, LineItem, Unit, Currency
from ksatria_muslim.invoice.models import WebhookTest


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


def webhook_test(request: HttpRequest):
    headers = request.headers, indent=2
    body = request.body
    post = request.POST

    WebhookTest.objects.create(headers=headers, body=body, post=post)
    return JsonResponse({"success": True})
