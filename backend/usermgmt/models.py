from django.db import models
from django.contrib.auth.models import Group

class Menu(models.Model):
    name = models.CharField(max_length=64, unique=True)
    path = models.CharField(max_length=128, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    groups = models.ManyToManyField(Group, blank=True, related_name='menus')

    def __str__(self):
        return self.name

# Create your models here.
