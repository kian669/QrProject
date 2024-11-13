# Generated by Django 5.1 on 2024-11-09 09:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrapp', '0023_alter_vehicle_student_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='student_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='qrapp.studentmasterlist'),
        ),
    ]
