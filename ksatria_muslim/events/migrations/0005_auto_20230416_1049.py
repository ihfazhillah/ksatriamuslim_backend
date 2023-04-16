# Generated by Django 3.2.13 on 2023-04-16 03:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_migrate_presenter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='migrated_presenter',
        ),
        migrations.AlterField(
            model_name='event',
            name='presenter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_presenters', to='events.eventpresenter'),
        ),
    ]
