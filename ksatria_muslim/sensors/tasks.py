import requests

from config import celery_app
from ksatria_muslim.sensors.di import sensors_composition_root
from ksatria_muslim.sensors.models import CCTVCamera


@celery_app.task()
def send_telegram(text):
    url = "https://api.telegram.org/bot6324872661:AAHMdxRtdPOWbmfvOuW4gHpeg3eOmPXSUQs/sendMessage"
    data = {"chat_id": "-1001376891793", "text": text}
    resp = requests.post(url, json=data)
    resp.close()


@celery_app.task(soft_time_limit=180, time_limit=180)
def record_and_send_video(cctv_label, caption):
    cctv = CCTVCamera.objects.filter(label=cctv_label).first()
    if not cctv:
        print("Cannot get cctv by it's label")
        return

    if cctv.is_busy:
        print("Cannot record, cctv is in busy state")
        return

    cctv.is_busy = True
    cctv.save()

    try:

        streamer = sensors_composition_root.streamer
        streamer.download(cctv.stream_url)
        streamer.concat_playlists()

        url = "https://api.telegram.org/bot6324872661:AAHMdxRtdPOWbmfvOuW4gHpeg3eOmPXSUQs/sendVideo"
        data = {"chat_id": "-1001376891793", "caption": caption}
        with open(streamer.output_file, "rb") as f:
            requests.post(url, data=data, files={"video": f.read()})

        streamer.clean()
    finally:
        cctv.is_busy = False
        cctv.save()

