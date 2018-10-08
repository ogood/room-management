from django.shortcuts import render
from rest_framework import viewsets,permissions
from .models import ParentProduct,Region,Product
from .serializers import ProductSerializer,ParentProductSerializer,DetailedParentSerializer,RegionSerializer
from rest_framework.response import Response
from .pagination import CustomPagination
class ParentProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for listing or retrieving Parent products.
    status of the products should be puclic
    """
    pagination_class = CustomPagination
    serializer_class = ParentProductSerializer
    def get_queryset(self):
        qs=ParentProduct.objects.filter(status='public')
        region=self.request.query_params.get("region",None)
        if region and len(region)<=12:
            try:
                int(region)
                qs=list(qs.raw("SELECT * FROM product_parentproduct WHERE region_path LIKE '{}%%' and status='public'".format(region)))
                return qs
            except (TypeError,ValueError):
                return qs.none()
        return qs.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DetailedParentSerializer(instance)
        return Response(serializer.data)
    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        region_all=self.request.query_params.get("region_all", None)
       # region=self.request.query_params.get("region",None)
        if region_all:
            serializer = RegionSerializer(Region.objects, many=True)
            return self.paginator.get_paginated_response(data,serializer.data)
        else:
            return self.paginator.get_paginated_response(data)

    
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for listing or retrieving Parent products.
    status of the products should be puclic
    """

    serializer_class = ProductSerializer
    def get_queryset(self):

        qs=Product.objects.filter(parent__status='public')
        return qs.all()


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for listing regions
    """
    pagination_class = None
    serializer_class = RegionSerializer
    def get_queryset(self):
        qs= Region.objects
        depth = self.request.query_params.get("depth", None)
        startswith=self.request.query_params.get("start", None)
        if depth and len(depth)==1:
            try:
                depth=int(depth)
                qs = qs.filter(depth=depth)
                return qs
            except (TypeError,ValueError):
                return qs.none()
        elif startswith and len(startswith)/4<=3:
            try:
                int(startswith)
                qs = qs.filter(path__startswith=startswith)
                return qs
            except (TypeError,ValueError):
                return qs.none()
        else:
            return qs
        return qs.none()


