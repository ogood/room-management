from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings

class SiteSettings(models.Model):
    name = models.CharField(
        "name", max_length=64, blank=False,null=False,
    )
    note = JSONField(blank=True,default={})
    def __str__(self):
        return self.name
class Application(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'submitted'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
        ('deleted', 'deleted'),
        ('initialed', 'initialed'),

    )
    title = models.CharField(
        "title", max_length=64, blank=False,null=False,default=''
    )
    owner= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='applications',blank=True,null=True)
    status=models.CharField(
        "status", max_length=16, choices=STATUS_CHOICES,blank=False,null=False,default='submitted'
    )
    note = models.TextField("note", blank=False,null=False,default=''
                                    )
    def __str__(self):
        return self.title
