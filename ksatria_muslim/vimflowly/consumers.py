from channels.generic.websocket import JsonWebsocketConsumer
from django.db import connection

from ksatria_muslim.vimflowly.middlewares import get_document


class VimFlowlyConsumer(JsonWebsocketConsumer):
    def receive_json(self, content, **kwargs):

        message_id = content.get("id")

        _type = content.get("type")

        if _type == "join":
            password = content.get("password")
            docname = content.get("docname")

            document_id = get_document(password, docname)
            if document_id:
                self.scope["document_id"] = document_id
                self.respond(message_id)
                self.send_json({"type": "joined", "clientId": content.get("clientId"), "docname": content.get("docname")})
            else:
                self.respond(message_id, error="Wrong password")

            return

        if _type == "get":
            key = content.get("key")
            with connection.cursor() as cursor:
                query = "select value from vimflowly_flowly where key = %s and document_id = %s"
                cursor.execute(query, [key, self.scope["document_id"]])
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

            query = "insert into vimflowly_flowly (key, value, document_id) values (%s, %s, %s) on conflict (key, document_id) do update set value = excluded.value"
            with connection.cursor() as cursor:
                cursor.execute(query, [key, value, self.scope["document_id"]])

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
