# Generated by Django 3.2.13 on 2023-07-06 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='token',
            field=models.CharField(default='', max_length=255),
        ),
    ]
