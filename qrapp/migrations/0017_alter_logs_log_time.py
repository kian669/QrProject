# Generated by Django 5.1 on 2024-10-27 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrapp', '0016_logs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logs',
            name='log_time',
            field=models.CharField(max_length=10),
        ),
    ]
