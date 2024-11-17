# Generated by Django 5.1 on 2024-11-16 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qrapp', '0027_delete_employee'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=255)),
                ('contact_number', models.CharField(max_length=15)),
                ('username', models.CharField(max_length=150, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('status', models.CharField(choices=[('regular', 'Regular'), ('contract', 'Contract of Service')], max_length=10)),
            ],
        ),
    ]
