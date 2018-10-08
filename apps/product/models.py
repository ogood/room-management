from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField,ArrayField
from django.conf import settings
from .models_region import *
from .models_order import *
from .models_bill import *
from .models_photo import *
import datetime
from django.db.models import Q
class ParentProduct(models.Model):
    STATUS_CHOICES = (
        ('default', _('default')),
        ('private', _('private')),
        ('rejected', _('rejected')),
        ('public', _('public')),
        ('deleted', _('deleted')),
        ('pending_review', _('pending review')),
    )
    TYPE_CHOICES = (
        ('condo', _('condo')),
        ('hostel', _('hostel')),
        ('relet', _('relet')),
    )
    PAY_CHOICES=(
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('semimonthly', _('Semimonthly')),
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('semiannually', _('Semiannually')),
        ('annually', _('Annually')),
    )
    name = models.CharField(
        _("name"), max_length=64, blank=True, default=''
        )

    type = models.CharField(
        _("Product structure"), max_length=24, choices=TYPE_CHOICES,
        null=False, blank=False, default='condo')
    structure = ArrayField(
        verbose_name=_("Structure"),base_field=models.IntegerField(),size=3,blank=True,default=[0,0,0])
    floor=ArrayField(
        verbose_name=_("Floor"),base_field=models.IntegerField(),size=2,blank=True,default=[0,0])

    region= models.ForeignKey(
        Region,
        on_delete=models.SET_DEFAULT,
        verbose_name=_("Region"),to_field='path',related_name='parent_products',db_column='region_path',default='')
    address = models.CharField(
        _("Address"), max_length=128, blank=True,default='')
    furnish = ArrayField(verbose_name=_("Furnish"), base_field=models.CharField(max_length=24, ), blank=True ,default=[])
    note = JSONField(blank=True,default={})
    status = models.CharField(
        _("Status"), max_length=64, choices=STATUS_CHOICES, default='')
    cover_photo=models.CharField(
        _("Cover Photo"), max_length=128, default='',blank=True)
    description = models.TextField(blank=True,default='')

    date_create = models.DateTimeField(_("Date created"), auto_now_add=True)
    date_update = models.DateTimeField(
        _("Date updated"), auto_now=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='parent_products',blank=True,default='')

    pay_cycle = models.CharField(
    _("Pay Cycle"),max_length=16,blank=True,choices=PAY_CHOICES, default="monthly")
    class Meta:

        app_label = 'product'
        ordering = ['-date_create']
        verbose_name = _('Parent Product')
        verbose_name_plural = _('Parent Products')


    def __str__(self):

        return self.name

    def get_absolute_url(self):
        """
        Return a product's absolute url
        """
        pass

    def clean(self):
        #getattr(self, '_clean_%s' % self.type)()
        pass

class Product(models.Model):
    STATUS_CHOICES = (
        ('available', _('available')),
        ('unavailable', _('unavailable')),
        ('private', _('private')),
        ('public', _('public')),
        ('rented', _('rented')),
        ('deleted', _('deleted')),
    )
    TYPE_CHOICES = (
        ('condo', _('condo')),
        ('single', _('single')),
    )
    PAY_CHOICES=(
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('semimonthly', _('Semimonthly')),
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('semiannually', _('Semiannually')),
        ('annually', _('Annually')),
    )
    name = models.CharField(
        _("name"), max_length=64, blank=True, default=''
        )
    type = models.CharField(
        _("Product type"), max_length=24, choices=TYPE_CHOICES,
        null=False, blank=False, default='single')
    structure = ArrayField(
        verbose_name=_("Structure"),base_field=models.IntegerField(),size=3,blank=True,default=[0,0,0])
    floor=ArrayField(
        verbose_name=_("Floor"),base_field=models.IntegerField(),size=2,blank=True,default=[0,0])
    price = models.FloatField(
        _("Monthly Rent"),null=False, blank=False,
        default=0)
    deposit = models.FloatField(
        _("deposit"),
        default=0)
    pay_cycle = models.CharField(
        _("Pay Cycle"),max_length=16,blank=True,choices=PAY_CHOICES, default="monthly")
    furnish = ArrayField(verbose_name=_("Furnish"), base_field=models.CharField(max_length=24, ), blank=True ,default=[])
    note = JSONField(blank=True,default={})
    status = models.CharField(
        _("Status"), max_length=64, choices=STATUS_CHOICES, default='')
    quantity = models.IntegerField(
        _("quantity"),blank=True,   default=1)
    date_create = models.DateTimeField(_("Date created"), auto_now_add=True)
    # This field is used by Haystack to reindex search
    date_update = models.DateTimeField(
        _("Date updated"), auto_now=True)
    parent = models.ForeignKey(
        'product.ParentProduct',
        on_delete=models.CASCADE,
        verbose_name=_("Parent"), related_name='children',)
    class Meta:
        app_label = 'product'
        ordering = ['name']
        verbose_name = _('Child Product')
        verbose_name_plural = _('Child Products')

    @property
    def owner(self):
        return self.parent.owner

    def __str__(self):
        return self.name
    def get_stock(self):#可出租的剩余量,[total quantity,available quantity]
       # return [self.quantity,self.quantity-self.orders.filter(Q(date_checkout__isnull=True)|Q(date_checkout__gte=datetime.date.today())).count()]
        return [self.quantity,self.quantity-self.orders.filter(status='ongoing').count()]
