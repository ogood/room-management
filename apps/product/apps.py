from django.apps import AppConfig

from django.db.models.signals import post_save

class ProductConfig(AppConfig):
    name="apps.product"
    def ready(self):
        from .signal_handles import share_group_bill,order_notify_renter
        from .models import GroupBill,RentOrder
        post_save.connect(share_group_bill, sender=GroupBill, weak=False)
        post_save.connect(order_notify_renter, sender=RentOrder, weak=False)


