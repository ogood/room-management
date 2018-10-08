from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings
from .models_order import *
class BillType:

    choices = [
        ('internet', _('internet')),
        ('electricity', _('electricity')),
        ('water', _('water')),
        ('gas', _('gas'))
    ]
    max_length=24
    @staticmethod
    def unshared_bill():

        return list(BillType.choices)
    @staticmethod
    def order_bill():
        d=BillType.choices+[('rental', _('rental'))]
        return list(d)
class Status:
    max_length = 24
    _order_bill=[
        ('draft',_('draft')),
        ('issued',_('issued')),
        ('claim_paid', _('claim paid')),
        ('confirm_paid', _('confirm paid')),
        ('deleted', _('deleted')),
    ]
    _group_bill=[
        ('draft', _('draft')),
        ('issued',_('issued')),
        ('confirm_paid', _('paid')),
        ('deleted', _('deleted')),
    ]

    @staticmethod
    def order():
        return list(Status._order)

    @staticmethod
    def order_bill():
        return list(Status._order_bill)

    @staticmethod
    def group_bill():
        return list(Status._group_bill)


class GroupBill(models.Model):
    product = models.ForeignKey(
        'product.ParentProduct',
        on_delete=models.CASCADE,
        related_name='original_bills',
        verbose_name=_("Product"))
    type=models.CharField(
        _("Bill type"), choices=BillType.unshared_bill(),max_length=BillType.max_length,
        null=False, blank=False, default=0)

    date_start = models.DateTimeField(
        _("start Date"), auto_now=False)
    date_end = models.DateTimeField(
        _("end Date"), auto_now=False)
    price = models.FloatField(
        _("Price"),
        blank=True, null=True)
    date_create = models.DateTimeField(
        _("Check in Date"), auto_now=True)
    note=JSONField(blank=True, null=True)
    status=models.CharField(
        _("Status"), choices=Status.group_bill(),max_length=Status.max_length,
        null=False, blank=False, default='')
    class Meta:
        app_label = 'product'
        ordering = ['-date_create']
    @property
    def owner(self):
        return self.product.owner

class RentBill(models.Model):

    rent_order = models.ForeignKey(
        RentOrder,
        on_delete=models.CASCADE,
        related_name='bills',
        verbose_name=_("Rent Order"))

    type=models.CharField(
        _("Bill type"), choices=BillType.order_bill(),max_length=BillType.max_length,
        default='')
    original_bill = models.ForeignKey(
        GroupBill,
        on_delete=models.CASCADE,
        related_name='shared_bills',
        verbose_name=_("Original Bill"),
        blank=True,null=True, default='')
    date_start = models.DateTimeField(
        _("Start Date"), auto_now=False)
    date_end = models.DateTimeField(
        _("End Date"), auto_now=False)
    date_create = models.DateTimeField(
        _("Created Date"), auto_now=True)
    note=JSONField(blank=True, default={})
    price = models.FloatField(
        _("Price"),default=0)
    status=models.CharField(
        _("bill status"), choices=Status.order_bill(),max_length=Status.max_length,
        null=False, blank=False, default='')

    @property
    def owner(self):
        return self.rent_order.product.parent.owner


    def __str__(self):
        return "a bill for an rent order."
    def display_dict(self):
        try:
            renter=self.rent_order.note["renter"]["nick_name"]
        except KeyError:
            renter="Unknown renter"
        data={
            "id":self.id,
            "room":self.rent_order.product.name,
            "renter":renter,
            "price":self.price,
            "date_start":self.date_start,
            "date_end":self.date_end,
        }
        return data

    class Meta:
        app_label = 'product'
        ordering = ['-date_create']
