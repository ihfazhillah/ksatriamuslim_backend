# Generated by Django 3.2.13 on 2024-03-11 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('children_task', '0002_task_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
