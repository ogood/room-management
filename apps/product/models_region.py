from django.db import models
from django.utils.translation import ugettext_lazy as _
class Region(models.Model):
    """
    Uses django-treebeard.
    """
    name = models.CharField(_('Name'), max_length=64)
    slug = models.SlugField(_('Slug'), max_length=32, db_index=True)
    path = models.CharField(max_length=32, unique=True)
    depth = models.PositiveIntegerField()
    class Meta:
        app_label = 'product'
    def __str__(self):
        return self.name
    def get_list_name(self):
        name=[]
        for i in range(int(len(self.path)/4)):
            region=Region.objects.get(path=self.path[0:i*4+4])
            name.append(region.name)
        return name
