# Generated by Django 5.1 on 2024-11-19 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrapp', '0035_employeeviolation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='course',
            field=models.CharField(choices=[('CAS', 'CAS'), ('COTE', 'COTE'), ('COMED', 'COMED'), ('CTE', 'CTE'), ('CGS', 'CGS')], max_length=100),
        ),
    ]
