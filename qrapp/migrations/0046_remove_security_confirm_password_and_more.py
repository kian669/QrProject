# Generated by Django 5.1 on 2025-01-05 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrapp', '0045_employee_created_at_studentmasterlist_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='security',
            name='confirm_password',
        ),
        migrations.AlterField(
            model_name='security',
            name='username',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
