from django.contrib.auth.models import User, Group
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class GroupStatus(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.group.name} - {'Active' if self.is_active else 'Inactive'}"
