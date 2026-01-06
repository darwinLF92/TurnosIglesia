from django.db import models
from django.contrib.auth.models import User  # Para el campo 'Creado_por'

class Establecimiento(models.Model):
    ESTADOS = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )
    
    nombre = models.CharField(max_length=255, verbose_name="Nombre Iglesia")
    hermandad = models.CharField(max_length=255, verbose_name="Nombre Hermandad")
    direccion = models.TextField(verbose_name="Dirección")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    sitio_web = models.URLField(blank=True, null=True, verbose_name="Sitio Web")
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name="Logo")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo', verbose_name="Estado")
    
    class Meta:
            verbose_name = "Establecimiento"
            verbose_name_plural = "Establecimientos"
            ordering = ['-fecha_creacion']

            # 👉 Permisos personalizados (ejemplos para tu menú)
            permissions = [
                ("acceso_mantenedor", "Acceso al menú Mantenedor"),
                ("acceso_establecimiento", "Acceso al módulo Establecimiento"),
                ("acceso_procesiones", "Acceso al módulo Procesiones"),
                ("acceso_turnos", "Acceso al módulo Turnos"),
                ("acceso_devotos", "Acceso al módulo Devotos"),
                ("acceso_inscripciones", "Acceso al módulo Inscripciones"),
                ("acceso_gestion_entrega", "Acceso a Gestión de Entrega de Turnos"),
                ("acceso_noticias", "Acceso al módulo Noticias"),
                ("crear_registro", "Puede Crear Registro"),
                ("editar_registro", "Puede Editar Registro"),
                ("inactivar_registo", "Puede Inactivar Registro"),
                ("eliminar_registro", "Puede Eliminar Registro"),
                ("abrir_reporte", "Puede Abrir Reporte"),
                ("exportar_reporte", "Puede Exportar Reporte"),
                ("crear_inscripcion", "Puede Crear Inscripción"),
                ("anular_inscripcion", "Puede Anular Inscripción"),
                ("entregar_turnos", "Puede Enttregar Turnos"),
                ("crear_publicacion", "Puede crear publicaciones"),
                ("editar_publicacion", "Puede editar publicaciones"),
                ("eliminar_publicacion", "Puede eliminar publicaciones"),
                ("turno_reservado", "Puede inscribir en turnos reservados"),
            ]
        
            def __str__(self):
             return self.nombre
