# Generated by Django 5.1 on 2024-11-09 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrapp', '0020_vehicle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='cr_upload',
            field=models.ImageField(upload_to='uploads/cr/'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='license_upload',
            field=models.ImageField(upload_to='uploads/license/'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='or_upload',
            field=models.ImageField(upload_to='uploads/or/'),
        ),
    ]
