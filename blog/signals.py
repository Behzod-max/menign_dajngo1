from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profil

@receiver(post_save, sender=User)
def profil_yaratish(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(foydalanuvchi=instance)

@receiver(post_save, sender=User)
def profil_saqlash(sender, instance, **kwargs):
    instance.profil.save()