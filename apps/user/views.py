from django.shortcuts import render
from rest_framework import viewsets
from apps.product.models import *
from django.contrib.auth.models import Group
from apps.site.models import Application
from apps.product.serializers import *
from .serializers import *
from rest_framework import status,exceptions
from rest_framework.response import Response
from apps.user.common import create_user_sms,verify_phone
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
import json
class RentOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for listing, retrieving rent orders .
    """
    serializer_class = RentOrderSerializer
    pagination_class = None
    def get_queryset(self):
        return RentOrder.objects.filter(renter=self.request.user.username).all()


class RentOrderBillViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for listing, retrieving rent orders .
    """
    serializer_class = RentBillSerializer
    pagination_class = None
    def get_queryset(self):
        return RentBill.objects.filter(rent_order_id=self.kwargs.get("order_pk",0),status="issued").all()


class ProfileViewSet(viewsets.mixins.RetrieveModelMixin,
                     viewsets.mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = UserSerializer
    queryset=User.objects.all()
    def get_object(self):
        return self.request.user

class ChangePasswordViewSet(viewsets.mixins.UpdateModelMixin,viewsets.GenericViewSet):
    """
    An view for changing password.
    """
    serializer_class=ChangePasswordSerializer
    def get_object(self, queryset=None):
        return self.request.user

    def change_password(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                raise exceptions.ParseError(detail="old password is wrong.")
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise exceptions.ParseError(detail="password not valid.")
class ChangeGroupViewSet(viewsets.mixins.UpdateModelMixin,viewsets.GenericViewSet):
    pass

class ChangeVerifyViewSet(viewsets.mixins.UpdateModelMixin,viewsets.GenericViewSet):
    """
    this api will be called when 'send verify code' is clicked
    """
    serializer_class=RegisterUserSerializer
    def get_object(self, queryset=None):
        return self.request.user
    def create(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            phone=serializer.validated_data.get("username",None)
            email=serializer.validated_data.get("email",None)
            if phone:
                return self.change_phone(request,serializer)
            elif email:
                return self.change_email(request,serializer)
            else:
                raise exceptions.ParseError(detail="you should provide email or phone.")
        raise exceptions.ParseError(detail="data not valid.")

    def change_phone(self, request,serializer):
        code=serializer.validated_data.get("verify_code",None)
        if code is None:
            verify_phone(serializer.validated_data['username'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if verify_phone(serializer.validated_data['username'],code):
                RentOrder.objects.filter(renter=self.object.username).update(renter=serializer.validated_data['username'])
                self.object.username=serializer.validated_data['username']
                self.object.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise exceptions.ParseError(detail="verify code not valid.")
    def change_email(self, request,serializer):
        code=serializer.validated_data.get("verify_code",None)
        if code is None:
            verify_phone(serializer.validated_data['email'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if verify_phone(serializer.validated_data['email'],code):
                self.object.username=serializer.validated_data['email']
                self.object.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise exceptions.ParseError(detail="verify code not valid.")




class RegisterViewSet(viewsets.GenericViewSet):
    """
    create an owner and send sms with password.
    if user already exist,user's password will be reset.
    """
    queryset = User.objects.none()
    serializer_class=RegisterUserSerializer
    def check_has_rent(self,phone):
        pass

    def create(self, request, *args, **kwargs):
        type=self.request.query_params.get('type',None)
        serializer = self.get_serializer(data=request.data)

        if type=='renter' or type=='reset_password':#创建一个崭新用户，默认为renter group
            serializer.is_valid(raise_exception=True)
            self.create_initial_user(request,serializer)
            #if RentOrder.objects.filter(renter=serializer.validated_data['username']).count()==0:
            #    raise exceptions.ParseError(detail="only open to renting tenant")

        elif type=='active_renter':
            serializer.is_renter_active_valid(raise_exception=True)
            self.create_renter(request,serializer, *args, **kwargs)
        elif type=='invite':#拥有邀请码的房东
            serializer.is_owner_form_valid(raise_exception=True)
            self.create_owner(request,serializer, *args, **kwargs)
        elif type=='fresh':#填写申请表的房东
            serializer.is_apply_owner_form_valid(raise_exception=True)
            Application.objects.create(title=serializer.validated_data['contact']+"-"+serializer.validated_data['username'],
                                       #owner=serializer.validated_data['username'],
                                       note=json.dumps(serializer.validated_data,ensure_ascii=False),
                                       status='submitted',
                                       )
        else:
            raise exceptions.ParseError(detail="register data error")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create_initial_user(self, request,serializer):
        #default group:renter
        if verify_phone(serializer.validated_data['username'],serializer.validated_data['verify_code']):
            try:
                user=User.objects.get(username=serializer.validated_data["username"])
                user.set_password(serializer.initial_data["password"])                
                user.save()
            except User.DoesNotExist:
                user=User.objects.create_user(username=serializer.validated_data['username'],\
                                            password=serializer.initial_data["password"],\
                                        # role='r--'
                                         )
                try:
                    user.groups.add(Group.objects.get(name='renter'))
                    user.groups.add(Group.objects.get(name='relet'))
                except Group.DoesNotExist:
                    raise exceptions.ParseError(detail="renter group not exist")

        else:
            raise exceptions.ParseError(detail="invalid phone number or verify code")
    def create_owner(self, request,serializer, *args, **kwargs):
        #serializer = self.get_serializer(data=request.data)
        if serializer.is_owner_form_valid(raise_exception=True):
            try:
                user=User.objects.get(username=serializer.validated_data["username"])
                user.groups.clear()
                user.groups.add(Group.objects.get(name='sublet'))
                #raise exceptions.ParseError(detail="user exists and altered as owner")
            except User.DoesNotExist:
                user=create_user_sms(serializer.validated_data["username"])# only owner role
                user.groups.add(Group.objects.get(name='sublet'))
            #return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.ParseError(detail="invitation code not valid.")

    def create_renter(self, request,serializer, *args, **kwargs):
        #check if the user has a renting record
        #serializer = self.get_serializer(data=request.data)
        if serializer.is_renter_active_valid(raise_exception=True):
            try:
                renter=User.objects.get(username=serializer.validated_data["username"])
                raise exceptions.ParseError(detail="renter exists already.")
            except User.DoesNotExist:
                pass
            try:
                owner=User.objects.get(username=serializer.initial_data["owner_phone"])
                orders=RentOrder.objects.filter(product__parent__owner=owner).filter(renter=serializer.validated_data["username"]).count()

                if orders>0:
                    renter=create_user_sms(serializer.validated_data["username"],
                            group='renter')# only owner role
                else:
                    raise exceptions.ParseError(detail="no rent record found to your phone number.")

            except User.DoesNotExist:
                raise exceptions.ParseError(detail="owner number doesn't exist.")
        else:
            raise exceptions.ParseError(detail="form not valid.")

class ObtainUserToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        response_dict=UserSerializer(user).data
        response_dict.update({'token': token.key,'role':'ro'})
        return Response(response_dict)

