# Generated by Django 4.2.18 on 2025-02-26 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_turnos', '0003_alter_registroinscripcion_inscrito'),
    ]

    operations = [
        migrations.AddField(
            model_name='registroinscripcion',
            name='fecha_entrega_estimada',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='registroinscripcion',
            name='lugar_entrega',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
