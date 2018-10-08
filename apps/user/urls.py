from rest_framework_nested import routers
from django.urls import include, path
from .views import *


#account/order
order_router = routers.SimpleRouter(trailing_slash=True)
order_router.register('order', RentOrderViewSet,base_name='rent-order')

#account/order/<order_pk>/bill
bill_router = routers.NestedSimpleRouter(order_router, r'order', lookup='order')
bill_router.register(r'bill', RentOrderBillViewSet, base_name='order-bill')


urlpatterns = [
    path('profile/', ProfileViewSet.as_view({'get': 'retrieve','patch':'partial_update'}),name="profile"),
path('register/', RegisterViewSet.as_view({'post': 'create'}),name="register"),

    path('change_verify/', ChangeVerifyViewSet.as_view({'post': 'create'}),name="change_verify"),

    path('change_password/', ChangePasswordViewSet.as_view({'put':'change_password'}),name="change-password"),

    path('', include(order_router.urls)),
   path('', include(bill_router.urls)),


]