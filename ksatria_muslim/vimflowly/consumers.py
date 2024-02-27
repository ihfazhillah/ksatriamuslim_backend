from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings
from ksatria_muslim.vimflowly.models import Flowly


class VimFlowlyConsumer(JsonWebsocketConsumer):
    def receive_json(self, content, **kwargs):

        print(content)

        password = settings.VIM_FLOWLY_PASSWORD
        message_id = content.get("id")

        _type = content.get("type")

        if _type == "join":
            if content.get("password") != password:
                self.respond(message_id, error="Wrong password")
                return

            self.respond(message_id)

        if _type == "get":
            data = Flowly.objects.get(key=message_id)
            self.respond(message_id, value=data.value)

        if _type == "set":
            Flowly.objects.update_or_create(defaults={"value": content.get("value")}, key=message_id)

    def respond(self, message_id, value = None, error = None):
        self.send_json({
            "type": "callback",
            "id": message_id,
            "result": {
                "value": value, "error": error
            }
        })
