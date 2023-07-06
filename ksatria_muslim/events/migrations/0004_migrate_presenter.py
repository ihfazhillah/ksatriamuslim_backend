# Generated by Django 3.2.13 on 2023-04-16 03:40

from django.db import migrations


def migrate_presenters(apps, schema_editor):
    presenter_model = apps.get_model("events", "EventPresenter")
    event = apps.get_model("events", "Event")

    for event in event.objects.all():
        presenter = event.presenter

        new_presenter, _ = presenter_model.objects.get_or_create(name=presenter.name)

        event.migrated_presenter = new_presenter
        event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20230416_1040'),
    ]

    operations = [
        migrations.RunPython(migrate_presenters, reverse_code=migrations.RunPython.noop)
    ]