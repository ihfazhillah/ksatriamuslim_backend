# Generated by Django 3.2.13 on 2023-08-26 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('irrigation', '0002_devicehistory_value_float'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicehistory',
            name='value_float',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='devicehistory',
            name='value_int',
            field=models.IntegerField(null=True),
        ),
    ]
