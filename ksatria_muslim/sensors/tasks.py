import requests

from config import celery_app


@celery_app.task()
def send_telegram(text):
    url = "https://api.telegram.org/bot6324872661:AAHMdxRtdPOWbmfvOuW4gHpeg3eOmPXSUQs/sendMessage"
    data = {"chat_id": "-1001376891793", "text": text}
    resp = requests.post(url, json=data)
    resp.close()
