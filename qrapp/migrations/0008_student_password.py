# Generated by Django 5.1 on 2024-09-28 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrapp', '0007_violation'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='password',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
