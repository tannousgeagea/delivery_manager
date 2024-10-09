# Generated by Django 4.2 on 2024-09-30 13:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0007_alter_deliverystate_delivery_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='metadatacolumn',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='metadatacolumn',
            name='metadata',
        ),
        migrations.AlterUniqueTogether(
            name='metadataflags',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='metadataflags',
            name='metadata',
        ),
        migrations.AlterUniqueTogether(
            name='metadatalocalization',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='metadatalocalization',
            name='metadata_column',
        ),
        migrations.DeleteModel(
            name='Metadata',
        ),
        migrations.DeleteModel(
            name='MetadataColumn',
        ),
        migrations.DeleteModel(
            name='MetadataFlags',
        ),
        migrations.DeleteModel(
            name='MetadataLocalization',
        ),
    ]