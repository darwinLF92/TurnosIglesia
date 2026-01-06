from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from inscripciones_online.models import DevotoCuenta 
from usuarios.models import UserProfile
from devotos.models import Devoto

User = get_user_model()


class Command(BaseCommand):
    help = "Crea Devoto y DevotoCuenta para usuarios existentes (si no existen)."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Simula sin guardar en BD.")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        creados_devoto = 0
        existentes_devoto = 0
        creados_cuenta = 0
        existentes_cuenta = 0
        conflictos = 0

        users = User.objects.all().select_related("perfil")
        self.stdout.write(self.style.NOTICE(f"Usuarios encontrados: {users.count()}"))
        if dry_run:
            self.stdout.write(self.style.WARNING("MODO DRY-RUN: No se guardará nada."))

        with transaction.atomic():
            for u in users:
                # 1) Asegurar perfil
                perfil = getattr(u, "perfil", None)
                if not perfil and not dry_run:
                    perfil = UserProfile.objects.create(user=u)

                # 2) Identificador único (CUI > email)
                cui = getattr(perfil, "cui", None) if perfil else None
                email = (u.email or "").strip() or None

                devoto = None

                # 3) Buscar Devoto existente
                if cui:
                    devoto = Devoto.objects.filter(cui_o_nit=cui).first()
                if not devoto and email:
                    devoto = Devoto.objects.filter(correo__iexact=email).first()

                # 4) Crear Devoto si no existe
                if not devoto:
                    nombre = ""
                    if perfil:
                        nombre = f"{perfil.nombres or ''} {perfil.apellidos or ''}".strip()
                    if not nombre:
                        nombre = u.username

                    data = dict(
                        nombre=nombre,
                        correo=email,
                        telefono=getattr(perfil, "telefono", "") or "",
                        direccion=getattr(perfil, "direccion", "") or "",
                        activo=True,
                        fecha_nacimiento=getattr(perfil, "fecha_nacimiento", None),
                        fotografia=getattr(perfil, "foto_perfil", None),
                        usuario_registro=u,
                    )

                    if cui:
                        data["cui_o_nit"] = cui

                    if dry_run:
                        creados_devoto += 1
                        # en dry-run no creamos realmente, saltamos DevotoCuenta
                        continue
                    else:
                        devoto = Devoto.objects.create(**data)
                        creados_devoto += 1
                else:
                    existentes_devoto += 1

                # 5) Crear DevotoCuenta si no existe
                #    (a) si ya existe para este user => ok
                if DevotoCuenta.objects.filter(user=u).exists():
                    existentes_cuenta += 1
                    continue

                #    (b) si el devoto ya está ligado a otro user => conflicto (no tocar)
                if DevotoCuenta.objects.filter(devoto=devoto).exists():
                    conflictos += 1
                    continue

                if dry_run:
                    creados_cuenta += 1
                else:
                    DevotoCuenta.objects.create(user=u, devoto=devoto)
                    creados_cuenta += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(f"Devotos creados: {creados_devoto}"))
        self.stdout.write(self.style.SUCCESS(f"Devotos ya existentes: {existentes_devoto}"))
        self.stdout.write(self.style.SUCCESS(f"DevotoCuenta creadas: {creados_cuenta}"))
        self.stdout.write(self.style.SUCCESS(f"DevotoCuenta ya existentes: {existentes_cuenta}"))
        self.stdout.write(self.style.WARNING(f"Conflictos (devoto ya ligado a otra cuenta): {conflictos}"))
