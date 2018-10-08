from django.db.models import Q
from datetime import datetime,timezone,timedelta
import math
from .models import *
def caculate_cross_days(start,end,checkin,checkout):
    if end<=checkin or start>=checkout:
        return 0

    if end <= checkout:
        if start<=checkin:
            td=end-checkin
        else:
            td=end-start
    elif end > checkout:
        if start<checkin:
            td=checkout-checkin
        else:
            td=checkout-start
    else:
        return -1
    return td.days

def share_group_bill(sender, instance,**kwargs):
    """
    when recieve a signal of saving an unshared bill,this function triggered and share the bill to all tenants.
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """


    child_list = []
    for object in instance.product.children.all():
        child_list.append("Q(product_id={})".format(object.pk))
    if child_list == []:
        return
    else:#select all orders belong to this parent product
        RentOrder_qs=RentOrder.objects.filter( eval("|".join(child_list))).all()

    days={}#select all ongong or check out date> bill start date
    orders=RentOrder_qs.filter(Q(date_checkout__isnull=True)|Q(date_checkout__gt=instance.date_start))
    if orders.count()>0:
        for order in orders.all():
            if order.date_checkout==None:
                order.date_checkout=order.date_contract_end
            cross_days=caculate_cross_days(instance.date_start,
                                                    instance.date_end,
                                                    order.date_checkin,
                                                    order.date_checkout)
            if cross_days>0:
                days[order]=cross_days
    total_days=sum([x for x in days.values()])
    for order in days:
        RentBill.objects.create(type=instance.type,
                                  date_start=order.date_checkin if order.date_checkin>=instance.date_start else instance.date_start,
                                  date_end=order.date_checkout if order.date_checkout <= instance.date_end else instance.date_end,
                                rent_order=order,
                                  original_bill=instance,
                                status=instance.status,
                                  price=math.ceil(instance.price*100/total_days*days[order])/100.0,

                                  )

def order_notify_renter(sender, instance,**kwargs):
    pass