from rest_framework import serializers
from apps.product.models import ParentProduct

class ParentProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentProduct
        fields = ('name',)