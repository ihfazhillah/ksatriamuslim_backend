from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings


class VimFlowlyConsumer(JsonWebsocketConsumer):
    def receive_json(self, content, **kwargs):
        from ksatria_muslim.vimflowly.models import Flowly

        password = settings.VIM_FLOWLY_PASSWORD
        message_id = content.get("id")

        _type = content.get("type")

        if _type == "join":
            if content.get("password") != password:
                self.respond(message_id, error="Wrong password")
                return

            self.respond(message_id)
            return

        if _type == "get":
            data = Flowly.objects.get(key=message_id)
            self.respond(message_id, value=data.value)
            return

        if _type == "set":
            Flowly.objects.update_or_create(defaults={"value": content.get("value")}, key=message_id)
            return

    def respond(self, message_id, value = None, error = None):
        self.send_json({
            "type": "callback",
            "id": message_id,
            "result": {
                "value": value, "error": error
            }
        })
