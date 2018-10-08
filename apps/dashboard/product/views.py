from rest_framework import viewsets
from apps.product.models import *
from apps.product.serializers import *
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from apps.helpers.permissions import ObjectOwnerMatch
from rest_framework import exceptions
from apps.user.common import welcome_renter
from rest_framework.parsers import MultiPartParser
from PIL import Image
from django.core.files.storage import get_storage_class
from datetime import datetime
import random,string
from rest_framework import status
from django.http import HttpResponse
import uuid
class ParentProductViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for listing, retrieving, updating, creating,deleting parent products .
    """
    permission_classes = (IsAuthenticated,ObjectOwnerMatch)
    serializer_class = DashboardParentSerializer
    max_create={'owner':30,'sublet':30,'relet':1}#must sort from largest to smallest
    def get_queryset(self):
        if self.request.user.is_superuser:
            return ParentProduct.objects.all()
        return self.request.user.parent_products.all()
    def get_serializer_class(self):
        #if self.request.query_params.get('type',None)=='relet':
        #    return ReletParentSerializer
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        #serializer=DashboardParentSerializer(instance)
        return Response(serializer.data)
    def check_max_create(self,user,threshold):
        count = ParentProduct.objects.filter(owner=user).count()
        for key in threshold:
            if key in user.get_groups():
                if self.max_create[key]>count:
                    return True#已经创建条目数小于最大限额
                else:
                    self.permission_denied(self.request, "You have reached the max count.")
        self.permission_denied(self.request, "You are not allowed to perform this action.")
    def create(self, request, *args, **kwargs):
        if self.request.query_params.get('type', None)=='relet':
            serializer = self.get_serializer(data=dict(request.data,type='relet'))
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        self.check_max_create(self.request.user,self.max_create)
        if self.request.user.is_superuser:
            pass
        elif serializer.validated_data["status"] == "public":#if the user create a public product, automatically set it to pending review
            serializer.validated_data["status"]="pending_review"
        elif serializer.validated_data["status"] == "private":
            pass
        else:
            self.permission_denied(self.request, "You are not allowed to perform this action.")
        type = self.request.query_params.get('type', None)
        if type=='relet':
            child=ProductSerializer(data={"type":self.request.data['type'],"price":self.request.data['price'],"deposit":self.request.data['deposit']})
            child.is_valid(raise_exception=True)
            product = serializer.save(owner=self.request.user)
            child.save(parent_id=product.id)
        else:
            product = serializer.save(owner=self.request.user)
        photos_wait=serializer.initial_data.get('add_photos',[])
        for photo in photos_wait:
            try:
                inst=ParentProductPhoto.objects.get(id=photo['id'])
                inst.product_id=product.id
                inst.save()
            except ParentProductPhoto.DoesNotExist:
                pass
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.type=='relet':
            serializer = self.get_serializer(instance,data=dict(request.data,type='relet'), partial=partial)
        else:
            serializer = self.get_serializer(instance,data=request.data, partial=partial)
        #serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            pass
        elif serializer.validated_data.get("status",None)==None:
            pass
        elif serializer.validated_data["status"] == "public":#if the user create a public product, automatically set it to pending review
            serializer.validated_data["status"]="pending_review"
        elif serializer.validated_data["status"] == "private":
            pass
        else:
            self.permission_denied(self.request, "You are not allowed to perform this action.")
        product=serializer.save()
        if product.type=='relet':
            child_instance=product.children.first()
            child=ProductSerializer(child_instance,data={"type":self.request.data['type'],"price":self.request.data['price'],"deposit":self.request.data['deposit']})
            child.is_valid(raise_exception=True)
            child.save()
        photos_wait=serializer.initial_data.get('add_photos',[])
        for photo in photos_wait:
            try:
                inst=ParentProductPhoto.objects.get(id=photo['id'])
                inst.product_id=product.id
                inst.save()
            except ParentProductPhoto.DoesNotExist:
                pass

    def perform_destroy(self, instance):
        for child in instance.children.all():
            child.delete()
        for photo in instance.photos.all():
            photo.delete()
        instance.delete()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ParentProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ParentProductSerializer(queryset, many=True)
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for listing, retrieving, updating, creating,deleting child products .
    """
    parent=None
    permission_classes = (IsAuthenticated,ObjectOwnerMatch)
    serializer_class = ProductSerializer
    def check_permissions(self, request):
        """
        check whether request is an owner
        check if request has permission to specific parent object.
        :param request:
        :return:None
        """
        super().check_permissions(request)
        parent_pk=self.kwargs['parent_pk']#the pk of this child's parent product
        try:
            self.parent=ParentProduct.objects.get(pk=parent_pk)
            if not self.request.user.is_superuser:
                assert self.parent.owner == self.request.user
        except (ParentProduct.DoesNotExist,AssertionError):
            self.permission_denied(self.request,"You can only edit your own poduct")

    def get_queryset(self):
        return self.parent.children.all()
    def check_object_permissions(self, request, obj):
        return True
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        type=self.request.query_params.get('type',None)
        if type=="many":
            serializer=self.perform_create_many(serializer)
        else:
            self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create_many(self, serializer):

        room_list=serializer.initial_data.get('room_list',[])
        basic_data={"structure":serializer.validated_data['structure']}
        for room in room_list:
            basic_data.update({"name": room['name'], "price": room['price'],"deposit":room['price']})
            serializer1 = self.get_serializer(data=basic_data)
            serializer1.is_valid(raise_exception=True)
            self.perform_create(serializer1)
        return serializer1
            
    def perform_create(self, serializer):
        product=serializer.save(parent_id=self.parent.pk)
        photos_wait=serializer.initial_data.get('add_photos',[])
        for photo in photos_wait:
            try:
                inst=ProductPhoto.objects.get(id=photo['id'])
                inst.product_id=product.id
                inst.save()
            except ProductPhoto.DoesNotExist:
                pass
    def perform_update(self, serializer):
        product=serializer.save()
        photos_wait=serializer.initial_data.get('add_photos',[])
        for photo in photos_wait:
            try:
                inst=ProductPhoto.objects.get(id=photo['id'])
                inst.product_id=product.id
            except ProductPhoto.DoesNotExist:
                pass

    def perform_destroy(self, instance):
        for photo in instance.photos.all():
            photo.delete()
        instance.delete()


class PhotoView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,ObjectOwnerMatch)

    def check_permissions(self, request):
        """
        check whether request is an owner
        check if request has permission to specific parent object.
        :param request:
        :return:None
        """
        super().check_permissions(request)
        self.path=self.request._request.path
        try:
            self.photo=ParentProductPhoto.objects.get(name=self.path)#target product belongs to editor
        except ParentProductPhoto.DoesNotExist:
            self.permission_denied(self.request,"You can only edit your own poduct")

        if self.photo.owner_id != self.request.user.pk:
            self.permission_denied(self.request,"You can only edit your own poduct")

    def retrieve(self, request, *args, **kwargs):
        response = HttpResponse()
        response['X-Accel-Redirect'] = "/internal"+self.path
        response['Content-Type'] = 'image/*'
        return response
        #header={'X-Accel-Redirect':"/internal"+self.path}
        #return Response({'':''},status=status.HTTP_200_OK, headers=header)

    def get_queryset(self):
        return ParentProductPhoto.all()


class PhotoUploader(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,ObjectOwnerMatch)
    parser_classes = (MultiPartParser,)
    def check_permissions(self, request):
        """
        check whether request is an owner
        check if request has permission to specific parent object.
        :param request:
        :return:None
        """
        super().check_permissions(request)
        self.product_pk=self.kwargs.get('filename',None)#target product
        self.which=self.request.query_params.get('for',None)
        self.permit=self.request.query_params.get('permit',None)
        if self.product_pk is '0':#create photos before product being created
            self.product_pk=None
            return
        elif self.which not in ('sub','parent'):
            self.permission_denied(self.request,"illegal parameters")
        try:
            if self.which=="parent":
                self.parent=ParentProduct.objects.get(pk=self.product_pk)#target product belongs to editor

            else:
                self.product=Product.objects.get(pk=self.product_pk)

        except (ParentProduct.DoesNotExist,AssertionError):
            self.permission_denied(self.request,"You can only edit your own poduct")

    def list(self, request, *args, **kwargs):
        return Response({'':''})

    def create(self, request, filename=None, format=None):
        files = request.FILES.getlist('imageFiles')
        dt = datetime.now()
        storage=get_storage_class()()
        list=[]
        """
        todo:valid image name.check if image name already exist in db/storage.
        """
        for file in files:#product id _ origin file name
            try:
                img_names=file.name.split(".")
                if img_names[-1].lower() not in ("png","jpeg","jpg","gif"):
                    raise exceptions.ParseError(detail="photo format not allowed")
                if self.permit == 'private':
                    random_str=str(uuid.uuid1())
                else:
                    random_str=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
                
                name=filename+'_'+random_str+"."+img_names[-1]
                
            except ValueError:
                self.permission_denied(self.request,"photo file name not allowed")
            if self.which=="sub":
                target=ProductPhoto
                if self.permit == 'private':
                    name_prefix = dt.strftime('private/%y%m/')
                else:
                    name_prefix=dt.strftime('room/%y%m/')
            else:
                target = ParentProductPhoto
                if self.permit == 'private':
                    name_prefix = dt.strftime('private/%y%m/')
                else:
                    name_prefix=dt.strftime('rooms/%y%m/')

            save_name=name_prefix+name#example : [private/]room/%y/%m/+ pk_xxxx.jpg
            #saved_name=storage.generate_filename(save_name)
            saved_name=storage.save(name=save_name,content=file)#example : media/[private/]room/%y/%m/+ pk_xxxx.jpg

            img=Image.open(storage.path(saved_name))
            if self.permit == 'private':
                img.thumbnail((800, 800))
            else:
                img.thumbnail((650,420))
            img.save(storage.path(saved_name))
            url_name=storage.url(saved_name)
           # try:
            #    target.objects.get(name=url_name)
            #except target.DoesNotExist:
            if self.permit == 'private':
                type='private'
            else:
                type='public'
            ins=target.objects.create(type=type,product_id=self.product_pk,name=url_name,owner=request.user)


            list.append({"id":ins.id,"url":ins.name})
        return Response(list)
    def get_object(self):

        self.photo_id = self.request.query_params.get('photo', None)
        if self.photo_id==None:
            raise exceptions.ParseError(detail="you must provide a valid photo id")
        if self.which=="sub":
            try:
                inst=ProductPhoto.objects.get(id=self.photo_id)
            except ProductPhoto.DoesNotExist:
                raise exceptions.NotFound(detail="photo not found")
        else:
            try:
                inst=ParentProductPhoto.objects.get(id=self.photo_id)
            except ParentProductPhoto.DoesNotExist:
                raise exceptions.NotFound(detail="photo not found")
        self.check_object_permissions(self.request, inst)
        return inst
    def perform_destroy(self, instance):
        #storage = get_storage_class()()
        #storage.delete(name=self.photo_name[7:])#to delete /media/ string
        instance.delete()

class RentOrderViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for listing, retrieving, updating, creating,deleting rent orders .
    """
    parent=None
    permission_classes = (IsAuthenticated,ObjectOwnerMatch)# no object permission control
    serializer_class = RentOrderSerializer


    def check_permissions(self, request):
        """
        check whether request is an owner
        check if request has permission to specific parent object.
        assign parent product to self object
        :param request:
        :return:None
        """
        super().check_permissions(request)
        parent_pk=self.kwargs.get('parent_pk',0)
        try:
            self.parent=ParentProduct.objects.get(pk=parent_pk)
            if not self.request.user.is_superuser:
                assert self.parent.owner == self.request.user
        except (ParentProduct.DoesNotExist,AssertionError):
            self.permission_denied(self.request,"You can only edit your own poduct")
        if self.action in ("update","partial_update"):
            if request.data=={}:
                return
            try:
                self.object=self.parent.children.get(orders__id=self.kwargs.get('pk',0))
            except Product.DoesNotExist:
                self.permission_denied(self.request, "You can only edit your own poduct")
        elif self.action=="create":
            if request.data=={}:
                return#so that to allow option request.
            try:
                product=self.parent.children.get(pk=request.data.get('product_id',0))
                if product.get_stock()[1]<1:
                    raise exceptions.ParseError(detail="failed:product out of stock")
            except Product.DoesNotExist:
                self.permission_denied(self.request, "You can only edit your own product")
    def get_queryset(self):
        child_pk=self.request.query_params.get('sub_pk',None)
        if child_pk:
            return RentOrder.objects.filter(product_id=child_pk).all()
        return RentOrder.objects.filter(product__parent=self.parent).all()
    def check_object_permissions(self, request, obj):
        return True
    def perform_create(self, serializer):
        #user=None
        '''
        try:
            if serializer.validated_data["note"]["renter"]["create_user"] is True:
                user=get_or_create_user(serializer.validated_data["note"]["renter"]["phone"],
                                        serializer.validated_data["note"]["renter"]["nick_name"],
                                        role='r--')
        except KeyError:
            pass
        '''
        if serializer.initial_data["notify_user"]==True:
            welcome_renter(serializer.validated_data["note"]["renter"]["phone"] )
        serializer.validated_data['renter']=serializer.validated_data["note"]["renter"]["phone"]
        serializer.validated_data["status"] = "ongoing"
        serializer.validated_data["date_contract_start"]=serializer.validated_data["date_contract_start"].replace(hour=12,minute=0)
        serializer.validated_data["date_contract_end"] = serializer.validated_data["date_contract_end"].replace(hour=12, minute=0)
        serializer.validated_data["date_checkin"] = serializer.validated_data["date_contract_start"]
        serializer.save()
    def perform_update(self, serializer):
        if serializer.initial_data.get("notify_user",None)==True:
            welcome_renter(serializer.validated_data["note"]["renter"]["phone"] )
        try:
            serializer.validated_data['renter']=serializer.validated_data["note"]["renter"]["phone"]
        except KeyError:
            pass
        if serializer.validated_data.get('date_checkout',None) is not None:
            serializer.save(status='checked_out')
        else:
            serializer.save()


class GroupBillViewSet(viewsets.ModelViewSet):
    """
    query and edit bills for parent product
    """
    parent=None
    permission_classes = (IsAuthenticated,ObjectOwnerMatch)
    serializer_class = GroupBillSerializer

    def check_permissions(self, request):
        """
        check whether request is an owner
        check if request has permission to specific parent object.
        :param request:
        :return:None
        """
        super().check_permissions(request)
        parent_pk=self.kwargs['parent_pk']
        try:
            self.parent=ParentProduct.objects.get(pk=parent_pk)
            if not self.request.user.is_superuser:
                assert self.parent.owner == self.request.user
        except (ParentProduct.DoesNotExist,AssertionError):
            self.permission_denied(self.request,"You can only edit your own product")
    def check_object_permissions(self, request, obj):
        return
    def get_queryset(self):
        return GroupBill.objects.filter(product_id=self.parent.pk).all()
    def perform_create(self, serializer):
        serializer.validated_data["product_id"]=self.kwargs['parent_pk']
        serializer.validated_data["status"]="issued"
        serializer.validated_data["date_start"]=serializer.validated_data["date_start"].replace(hour=12,minute=0)
        serializer.validated_data["date_end"] = serializer.validated_data["date_end"].replace(hour=12, minute=0)
        serializer.save()

class RentBillViewSet(viewsets.ModelViewSet):
    """
    /query and edit bills for order. support child product query. +?sub_pk= & order_pk=
    this api will be dropped.
    """
    parent=None
    product=None
    permission_classes = (IsAuthenticated,ObjectOwnerMatch)
    serializer_class = RentBillSerializer

    def check_permissions(self, request):
        """
        check whether request is an owner
        check if request has permission to specific parent object.
        :param request:
        :return:None
        """
        super().check_permissions(request)
        parent_pk=self.kwargs['parent_pk']
        try:
            self.parent=ParentProduct.objects.get(pk=parent_pk)
            if not self.request.user.is_superuser:
                assert self.parent.owner == self.request.user
           # self.product=RentBillSerializer.objects.get(pk=self.product.pk)
           # assert self.product.parent==self.parent
        except (ParentProduct.DoesNotExist,RentBill.DoesNotExist,AssertionError):
            self.permission_denied(self.request,"You can only edit your own product")
    def check_object_permissions(self, request, obj):
        return
    def get_queryset(self):
        child_pk=self.request.query_params.get('sub_pk',None)
        if child_pk:
            return RentBill.objects.filter(rent_order__product_id=child_pk).all()
        order_pk = self.request.query_params.get('order_pk', None)
        if order_pk:
            return RentBill.objects.filter(rent_order_id=order_pk).all()

        return RentBill.objects.filter(rent_order__product__parent=self.parent).all()
    def perform_create(self, serializer):
        serializer.validated_data["rent_order_id"]=self.kwargs['order_pk']
        serializer.validated_data["date_start"]=serializer.validated_data["date_start"].replace(hour=12,minute=0)
        serializer.validated_data["date_end"] = serializer.validated_data["date_end"].replace(hour=12, minute=0)
        serializer.validated_data["status"]="issued"
        serializer.save()

class RentOrderBillViewSet(viewsets.ModelViewSet):
    """
    query and edit bills of child product,via order pk
    """
    parent=None
    product=None
    permission_classes = (IsAuthenticated,ObjectOwnerMatch)
    serializer_class = RentBillSerializer

    def check_permissions(self, request):
        """
        check whether request is an owner
        check if request has permission to specific parent object.
        :param request:
        :return:None
        """
        super().check_permissions(request)
        parent_pk=self.kwargs['parent_pk']
        try:
            self.parent=ParentProduct.objects.get(pk=parent_pk)
            if not self.request.user.is_superuser:
                assert self.parent.owner == self.request.user
           #todo: check if have permission to view the rent order
           # self.product=Product.objects.get(pk=self.kwargs['rent_order_pk'])
           # assert self.product.parent==self.parent
        except (ParentProduct.DoesNotExist,RentBill.DoesNotExist,AssertionError):
            self.permission_denied(self.request,"You can only edit your own product")
    def check_object_permissions(self, request, obj):
        return
    def get_queryset(self):
        return RentBill.objects.filter(rent_order__id=self.kwargs.get('rent_order_pk',0)).all()

    def perform_create(self, serializer):
        serializer.validated_data["rent_order_id"]=self.kwargs['rent_order_pk']
        serializer.validated_data["status"]="issued"
        serializer.validated_data["date_start"]=serializer.validated_data["date_start"].replace(hour=12,minute=0)
        serializer.validated_data["date_end"] = serializer.validated_data["date_end"].replace(hour=12, minute=0)
        serializer.save()
