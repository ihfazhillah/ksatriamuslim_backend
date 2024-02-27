import json

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
            self.send_json({"type": "joined", "clientId": content.get("clientId"), "docname": content.get("docname")})
            return

        if _type == "get":
            key = content.get("key")
            try:
                data = Flowly.objects.get(key=key)
                self.respond(message_id, value=data.value)
            except Flowly.DoesNotExist:
                self.respond(message_id, value="null")
            return

        if _type == "set":
            try:
                key = content.get("key")
                value = content.get("value")

                if key == "save:lastID":
                    value = int(value)

                if key.endswith("children"):
                    value = json.loads(value)
                    value = [int(v) for v in value]

                if key.endswith("parent"):
                    value = json.loads(value)
                    value = [int(v) for v in value]

                Flowly.objects.update_or_create(defaults={"value": value}, key=key)
                self.respond(message_id)
                return
            except Exception as e:
                self.respond(message_id, error=str(e))
                return

    def respond(self, message_id, value = None, error = None):
        result = {"error": error}
        if value is not None:
            result["value"] = value

        self.send_json({
            "type": "callback",
            "id": message_id,
            "result": result
        })
