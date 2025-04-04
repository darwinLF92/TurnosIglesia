# Generated by Django 5.1.1 on 2025-03-25 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devotos', '0006_devoto_fecha_eliminacion_devoto_fecha_modificacion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devoto',
            name='correo',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='devoto',
            name='edad',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
