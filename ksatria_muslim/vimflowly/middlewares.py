from django.db import connection


def get_document(key, document_name):
    query = "select id from vimflowly_document where key=%s and document_name=%s"

    with connection.cursor() as cursor:
        cursor.execute(query, [key, document_name])
        row = cursor.fetchone()
        if row:
            return row[0]
