# Generated by Django 3.2.13 on 2024-03-25 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('children_task', '0004_tikrar_tikraritem'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='detail',
            field=models.JSONField(default={}),
        ),
        migrations.AddField(
            model_name='task',
            name='type',
            field=models.CharField(choices=[('yesno', 'yesno'), ('need_verification', 'need_verification'), ('tikrar', 'tikrar')], default='yesno', max_length=255),
        ),
    ]
