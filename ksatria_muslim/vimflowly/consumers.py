import json

from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings
from django.db import connection


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
            with connection.cursor() as cursor:
                query = "select value from vimflowly_flowly where key = %s"
                cursor.execute(query, [key])
                row = cursor.fetchone()
                if row:
                    self.respond(message_id, value=row[0])
                else:
                    self.respond(message_id, value="null")
            return

        if _type == "set":
            key = content.get("key")
            value = content.get("value")

            # if key == "save:lastID":
            #     value = int(value)
            #
            # if key.endswith("children"):
            #     value = json.loads(value)
            #     value = [int(v) for v in value]
            #
            # if key.endswith(":parent"):
            #     value = json.loads(value)
            #     value = [int(v) for v in value]

            query = "insert into vimflowly_flowly (key, value) values (%s, %s) on conflict (key) do update set value = excluded.value"
            with connection.cursor() as cursor:
                cursor.execute(query, [key, value])

            self.respond(message_id)
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
