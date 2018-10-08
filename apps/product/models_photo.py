from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import get_storage_class
from django.conf import settings

class ProductPhoto(models.Model):
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name=_("Product"),null=True)
    name = models.CharField(
        _("name"),max_length=128,null=True)
    date_create = models.DateTimeField(
        _("Create Date"), auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ProductPhotos',
        verbose_name=_("Owner"),default=1)
    type=models.CharField(
        _("type"),max_length=16,default='public')
    class Meta:
        ordering = ['-date_create']


    def delete(self, using=None, keep_parents=False):
        storage=get_storage_class()()
        if storage.exists(self.name[7:]):
            storage.delete(self.name[7:])
        super().delete(using,keep_parents)
class ParentProductPhoto(models.Model):
    product = models.ForeignKey(
        'product.ParentProduct',
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name=_("ParentProduct"),null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ParentPhotos',
        verbose_name=_("Owner"),default=1)
    name = models.CharField(
        _("name"),max_length=128,null=True)
    date_create = models.DateTimeField(
        _("Create Date"), auto_now=True)
    type=models.CharField(
        _("type"),max_length=16,default='public')



    class Meta:
        ordering = ['-date_create']
    def delete(self, using=None, keep_parents=False):
        storage=get_storage_class()()
        if self.name[7:]!='' and storage.exists(self.name[7:]):
            storage.delete(self.name[7:])
        if self.product.cover_photo==self.name:
            self.product.cover_photo==''
            self.product.save()
        super().delete(using,keep_parents)