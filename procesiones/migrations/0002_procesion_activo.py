# Generated by Django 5.1.1 on 2024-09-16 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procesiones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='procesion',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]
