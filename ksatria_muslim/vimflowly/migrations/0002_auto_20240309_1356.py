# Generated by Django 3.2.13 on 2024-03-09 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vimflowly', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
                ('key', models.CharField(max_length=255)),
                ('document_name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='flowly',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vimflowly.document'),
        ),
    ]
