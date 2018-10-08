
from django.urls import include, path,re_path
from django.views.generic import TemplateView


urlpatterns = [
    path('api/product/', include(('apps.product.urls','apps.product'), namespace='product')),
    path('api/manage/', include(('apps.dashboard.urls','apps.dashboard'),namespace='dashboard')),
    path('api/account/', include(('apps.user.urls','apps.user'),namespace='account')),

    re_path(r'^manage/', TemplateView.as_view(template_name="manage.html")),
    re_path(r'^account/', TemplateView.as_view(template_name="manage.html")),
    path('login/', TemplateView.as_view(template_name="manage.html")),
    path('logout/', TemplateView.as_view(template_name="manage.html")),
    path('register/', TemplateView.as_view(template_name="manage.html")),
    path('active_renter/', TemplateView.as_view(template_name="manage.html")),
    path('owner_register/', TemplateView.as_view(template_name="manage.html")),


    path('m/', TemplateView.as_view(template_name="list.html")),
    path('m/rooms/<int:id>/', TemplateView.as_view(template_name="list.html")),
    path('m/room/<int:id>/', TemplateView.as_view(template_name="list.html")),
    path('', TemplateView.as_view(template_name="listing.html")),
    path('rooms/<int:id>/', TemplateView.as_view(template_name="listing.html")),


]
