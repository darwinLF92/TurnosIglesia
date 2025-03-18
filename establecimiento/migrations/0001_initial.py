# Generated by Django 4.2.18 on 2025-01-20 18:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Establecimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255, verbose_name='Nombre')),
                ('direccion', models.TextField(verbose_name='Dirección')),
                ('telefono', models.CharField(max_length=20, verbose_name='Teléfono')),
                ('email', models.EmailField(max_length=254, verbose_name='Correo Electrónico')),
                ('sitio_web', models.URLField(blank=True, null=True, verbose_name='Sitio Web')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logos/', verbose_name='Logo')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('estado', models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], default='activo', max_length=10, verbose_name='Estado')),
                ('creado_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Creado por')),
            ],
            options={
                'verbose_name': 'Establecimiento',
                'verbose_name_plural': 'Establecimientos',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]
