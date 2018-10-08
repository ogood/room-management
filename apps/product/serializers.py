from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model

class ProductSerializer(serializers.ModelSerializer):
    stock=serializers.SerializerMethodField()#extra field, display how many left.
    photos = serializers.SerializerMethodField()
    parent_name=serializers.SerializerMethodField()
    owner=serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    area=serializers.SerializerMethodField()
    region=serializers.SerializerMethodField()
    note=serializers.SerializerMethodField()
    class Meta:
        model = Product
        exclude = ('quantity','date_create', 'date_update',)
        read_only_fields=('parent','owner','photos')
    def get_photos(self,obj):
        data=[]
        for photo in obj.photos.all():
            data.append({"id":photo.id,"url":photo.name})
        return data

    def get_stock(self,obj):
        """
        :param obj:
        :return: total,available rooms count
        """
        return obj.get_stock()
    def get_address(self,obj):
        return obj.parent.address
    def get_parent_name(self,obj):
        return obj.parent.name
    def get_owner(self,obj):
        data={
            'name':obj.parent.owner.nick_name,
            'phone':obj.parent.owner.username
        }
        return data
    def get_region(self,obj):
        return obj.parent.region.path
    def get_area(self,obj):
        return obj.parent.region.get_list_name()
    def get_note(self,obj):
        note={}
        note["bmap"]=obj.parent.note.get("bmap",{})
        note["label"]=obj.parent.note.get("label",[])
        return note

class ParentProductSerializer(serializers.ModelSerializer):
    region = serializers.SlugRelatedField(
        queryset=Region.objects.all(),
        many=False,
        slug_field='path',
        required=True
     )
    stock=serializers.SerializerMethodField()#extra field, display how many left.
    price_range=serializers.SerializerMethodField()#extra field, display how many left.
    owner = serializers.SerializerMethodField()
    class Meta:
        model = ParentProduct
        exclude = ('date_create', 'date_update','note','furnish')
    def get_owner(self,obj):
        data={
            'name':obj.owner.nick_name,
            'phone':obj.owner.username
        }
        return data
    def get_price_range(self,obj):
        """
        :param obj:
        :return:[lowest price, highest price]
        """
        range=[0,0]
        for index,room in enumerate(obj.children.all()):
            if index==0:
                range[0]=room.price
                range[1]=room.price
            if room.price<range[0]:
                range[0]=room.price
            if room.price>range[1]:
                range[1]=room.price
        return range


    def get_stock(self,obj):
        """
        :param obj:
        :return: a list,[total rooms count,available rooms count]
        """
        stock=[0,0]

        for room in obj.children.all():
            quantity=room.get_stock()
            stock[0] += quantity[0]
            stock[1] += quantity[1]
        return stock

class DetailedParentSerializer(ParentProductSerializer):
    children=ProductSerializer(many=True, read_only=True)
    photos = serializers.SerializerMethodField()

    area=serializers.SerializerMethodField()


    class Meta:
        model = ParentProduct
        exclude = ('date_create', 'date_update','furnish')
        read_only_fields=('owner','photos')

    def get_child_photos(self,obj):
        data=[]
        for child in obj.children.all():
            for photo in child.photos.all():
                data.append(photo.name)
        return data

    def get_area(self,obj):
        return obj.region.get_list_name()
    def get_photos(self,obj):
        data=[]
        for photo in obj.photos.filter(type='public').all():
            data.append({"id":photo.id,"url":photo.name})
        return data

class DashboardParentSerializer(DetailedParentSerializer):
    private_photos = serializers.SerializerMethodField()
    def get_private_photos(self,obj):
        data=[]
        for photo in obj.photos.filter(type='private').all():
            data.append({"id":photo.id,"url":photo.name})
        return data

class ReletParentSerializer(DashboardParentSerializer):
    price = serializers.SerializerMethodField()
    deposit = serializers.SerializerMethodField()
    def get_price(self,obj):
        return obj.children.first().price
    def get_deposit(self,obj):
        return obj.children.first().deposit

class RentOrderSerializer(serializers.ModelSerializer):
    product=serializers.StringRelatedField(many=False,read_only=True)
    product_id=serializers.CharField()
    renter =serializers.SerializerMethodField()
    class Meta:
        model = RentOrder
        exclude = ('date_create','status')
       # read_only_fields=('renter',)
    def get_renter(self,obj):
        if obj.renter and len(obj.renter)>10:
            renter=get_user_model().objects.filter(username=obj.renter).first()
            if renter:
                return {"nick_name":renter.nick_name,
                    "phone":renter.username
                    }
        else:
            return None


class DictRelatedField(serializers.RelatedField):
    """
    A field that represents its targets using their
    display_dict out put.
    """
    def to_representation(self, value):
        return value.display_dict()

class RentBillSerializer(serializers.ModelSerializer):

    class Meta:
        model = RentBill
        exclude = ('note', 'original_bill','rent_order','status')

class GroupBillSerializer(serializers.ModelSerializer):
    shared_bills=DictRelatedField(many=True,read_only=True)
    #shared_bills=RentBillSerializer(many=True, read_only=True)
    class Meta:
        model = GroupBill
        exclude = ('note', 'status','product')




class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = '__all__'

