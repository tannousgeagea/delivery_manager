# Generated by Django 4.2 on 2024-09-05 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0003_metadatacolumn_description_metadataflags_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='metadatacolumn',
            name='description',
        ),
        migrations.AlterField(
            model_name='metadataflags',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
