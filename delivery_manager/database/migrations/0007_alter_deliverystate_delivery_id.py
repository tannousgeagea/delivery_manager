# Generated by Django 4.2 on 2024-09-30 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0006_alter_deliverystate_delivery_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverystate',
            name='delivery_id',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
