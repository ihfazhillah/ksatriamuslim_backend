# Generated by Django 3.2.13 on 2024-01-13 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeentry',
            name='ref_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='timeentry',
            name='ref_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
