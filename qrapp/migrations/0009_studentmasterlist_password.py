# Generated by Django 5.1 on 2024-09-28 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrapp', '0008_student_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentmasterlist',
            name='password',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
