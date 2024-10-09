# Generated by Django 4.2 on 2024-10-08 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0008_alter_metadatacolumn_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverystate',
            name='delivery_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('on-going', 'Active'), ('done', 'Done')], default='pending', max_length=255),
        ),
    ]
