# Generated by Django 3.2.13 on 2024-01-14 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0004_auto_20240114_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='webhooktest',
            name='post',
            field=models.TextField(blank=True, null=True),
        ),
    ]