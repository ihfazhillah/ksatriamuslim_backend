# Generated by Django 3.2.13 on 2024-02-27 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Flowly',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.TextField(db_index=True, unique=True)),
                ('value', models.TextField()),
            ],
        ),
    ]
