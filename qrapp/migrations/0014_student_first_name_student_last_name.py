# Generated by Django 5.1 on 2024-10-27 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrapp', '0013_studentmasterlist_first_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
