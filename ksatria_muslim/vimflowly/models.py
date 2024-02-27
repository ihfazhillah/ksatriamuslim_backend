from django.db import models


class Flowly(models.Model):
    key = models.TextField(unique=True, db_index=True)
    value = models.TextField()
