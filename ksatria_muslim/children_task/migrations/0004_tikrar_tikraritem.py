# Generated by Django 3.2.13 on 2024-03-25 16:32

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('children_task', '0003_task_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tikrar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(max_length=255)),
                ('max_tikrar', models.IntegerField(default=3)),
                ('version', models.IntegerField(default=1)),
                ('generated_file', models.FileField(blank=True, null=True, upload_to='tikrar/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TikrarItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('index', models.IntegerField(default=0)),
                ('text', models.TextField()),
                ('audio', models.FileField(upload_to='tikrar-audio/')),
                ('tikrar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='children_task.tikrar')),
            ],
            options={
                'ordering': ['index'],
            },
        ),
    ]
