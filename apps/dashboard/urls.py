from rest_framework_nested import routers
from django.urls import include, path
from .product import views as DashboardProductViews

dashboard = routers.SimpleRouter(trailing_slash=True)
dashboard.register('product', DashboardProductViews.ParentProductViewSet,base_name='parent-product')
#product/<parent_pk>/sub
child_router = routers.NestedSimpleRouter(dashboard, r'product', lookup='parent')
child_router.register(r'sub', DashboardProductViews.ProductViewSet, base_name='child-product')
#product/<parent_pk>/order
parent_order_router = routers.NestedSimpleRouter(dashboard, r'product', lookup='parent')
parent_order_router.register(r'order', DashboardProductViews.RentOrderViewSet, base_name='parent-order')
#product/<parent_pk>/bill
parent_bill_router = routers.NestedSimpleRouter(dashboard, r'product', lookup='parent')#group bill
parent_bill_router.register(r'bill', DashboardProductViews.GroupBillViewSet, base_name='parent-bill')
#product/<parent_pk>/rentbill
rent_bill_router = routers.NestedSimpleRouter(dashboard, r'product', lookup='parent')#group bill
rent_bill_router.register(r'rentbill', DashboardProductViews.RentBillViewSet, base_name='parent-bill')

#product/<parent_pk>/order/<rent_order_pk>/bill
rent_order_bill_router = routers.NestedSimpleRouter(parent_order_router, r'order', lookup='rent_order')#
rent_order_bill_router.register(r'bill', DashboardProductViews.RentOrderBillViewSet, base_name='rent-order-bill')

urlpatterns = [
    path('', include(dashboard.urls)),
    path('', include(child_router.urls)),
    path('', include(parent_order_router.urls)),
    path('', include(parent_bill_router.urls)),
    path('', include(rent_order_bill_router.urls)),
    path('', include(rent_bill_router.urls)),
    path('upload/<str:filename>',DashboardProductViews.PhotoUploader.as_view({'delete':'destroy','post':'create'})),

]