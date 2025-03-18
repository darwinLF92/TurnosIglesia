# Generated by Django 4.2.18 on 2025-03-17 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aplicacion', '0004_imagenpresentacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='marchafunebre',
            name='duracion',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='marchafunebre',
            name='favoritos',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='marchafunebre',
            name='imagen_portada',
            field=models.ImageField(blank=True, null=True, upload_to='marchas_funebres/portadas/'),
        ),
    ]
