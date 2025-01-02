# Generated by Django 5.1 on 2024-12-03 05:33

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrapp', '0043_remove_employeependingregistration_qr_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeLogs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('log_type', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout')], max_length=10)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='qrapp.employee')),
            ],
        ),
    ]
