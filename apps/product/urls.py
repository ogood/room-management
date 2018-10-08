from rest_framework_nested import routers
from . import views as ProductViews

product = routers.SimpleRouter(trailing_slash=True)
#/product/region
product.register(r'region', ProductViews.RegionViewSet,base_name='region')#parent-product-list ,parent-product-detail

#product/<pk>/
product.register(r'', ProductViews.ParentProductViewSet,base_name='parent-product')#parent-product-list ,parent-product-detail


#product/sub/<pk>/
product.register(r'sub', ProductViews.ProductViewSet,base_name='child-product')#parent-product-list ,parent-product-detail

#product/<parent_pk>/order
urlpatterns = product.urls
