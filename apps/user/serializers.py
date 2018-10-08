from rest_framework import serializers
from .models import *
from django.contrib.auth.password_validation import validate_password
from apps.site.models import SiteSettings
import re
class UserSerializer(serializers.ModelSerializer):
    groups=  serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        read_only=True,

     )
    class Meta:
        model = User
        fields = ('nick_name', 'username','email','groups','is_staff','is_superuser')
        read_only_fields=('username','email','groups','is_staff','is_superuser')

class RegisterUserSerializer(serializers.Serializer):
    """
    Serializer for chaging password.
    """
    username = serializers.CharField(required=True)
    email=serializers.EmailField(required=False)
    verify_code=serializers.RegexField('^\d{4}$',required=False)
    invitation_code = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    other = serializers.CharField(required=False)
    contact = serializers.CharField(required=False)
    def is_owner_form_valid(self, raise_exception=False):
        super().is_valid(raise_exception)
        phone_re=re.compile('^1\d{10}')
        if phone_re.match(self.validated_data['username']) is False:
            return False

        try:#字段name:invitation_code,字段note：json对象，其中包含code_list数组
            invi_code=SiteSettings.objects.get(name="invitation_code")
            if self.validated_data['invitation_code'] not in invi_code.note["code_list"]:
                return False
        except SiteSettings.DoesNotExist:
            return False
        return True
    def is_apply_owner_form_valid(self, raise_exception=False):
        super().is_valid(raise_exception)
        phone_re=re.compile('^1\d{10}')
        if phone_re.match(self.validated_data['username']) is False:
            return False
        return True
    def is_renter_active_valid(self, raise_exception=False):
        super().is_valid(raise_exception)
        phone_re=re.compile('^1\d{10}')
        if phone_re.match(self.validated_data['username']) is False:
            return False
        if phone_re.match(self.initial_data['owner_phone']) is False:
            return False
        price_re=re.compile('^\d{3,6}$')
        if phone_re.match(self.initial_data['price']) is False:
            return False
        return True

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for chaging password.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
