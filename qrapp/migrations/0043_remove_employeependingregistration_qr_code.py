# Generated by Django 5.1 on 2024-11-29 18:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qrapp', '0042_employeependingregistration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeependingregistration',
            name='qr_code',
        ),
    ]
