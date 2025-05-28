from django.db import models
from django.contrib.auth.models import Group, User

class Menu(models.Model):
    name = models.CharField(max_length=64, unique=True)
    path = models.CharField(max_length=128, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    groups = models.ManyToManyField(Group, blank=True, related_name='menus')

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # 若 profile 不存在则自动创建
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance)
        else:
            instance.profile.save()

# Create your models here.
