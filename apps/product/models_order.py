from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings

class Status:
    max_length = 24
    _order = [
        ('ongoing', _('ongoing')),
        ('checked_out', _('checked out')),
        ('deleted', _('deleted')),
    ]


    @staticmethod
    def order():
        return list(Status._order)
class RentOrder(models.Model):
    PAY_CHOICES=(
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('semimonthly', _('Semimonthly')),
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('semiannually', _('Semiannually')),
        ('annually', _('Annually')),
    )
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_("Product"))

    renter = models.CharField(
    _("Renter"),max_length=24,blank=True,null=False, default="")

    price = models.FloatField(
        _("Monthly Rent"),
        blank=True, default=0)
    deposit = models.FloatField(
        _("Deposit "),
        blank=True, default=0)
    pay_cycle = models.CharField(
        _("Pay Cycle"),max_length=16,blank=True,choices=PAY_CHOICES, default="monthly")
    due_day=models.IntegerField(_("Due day"),default=1)
    date_contract_start= models.DateTimeField(
        _("Contract start"), auto_now=False)

    date_contract_end= models.DateTimeField(
        _("Contract end"), auto_now=False)

    date_checkin = models.DateTimeField(
        _("Check in Date"), auto_now=False,null=True)
    date_checkout = models.DateTimeField(
        _("Check out Date"), auto_now=False,null=True,blank=True)

    date_create = models.DateTimeField(
        _("Check in Date"), auto_now=True)
    note=JSONField(blank=True, null=False,default={})

    status=models.CharField(
        _("order status"), choices=Status.order(),max_length=Status.max_length,
        null=False, blank=False, default='')
    @property
    def owner(self):
        return self.product.parent.owner

    def get_renter(self):
        return self.renter
    def __str__(self):
        return self.product.name
    class Meta:

        app_label = 'product'
        ordering = ['-date_contract_start']

