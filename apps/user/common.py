from apps.user.models import User
import random
import json
from apps.helpers.sms.send_q import sms_login_info,sms_welcome_renter,sms_verify_code
from rest_framework import exceptions
from django.core.cache import cache


def create_user_sms(username,nick_name='',pw=None):
    """
    username of model is phone number actually
    """
    if pw is None:
        pw=User.objects.make_random_password(length=6,allowed_chars='abcdefghjkmnpqrstuvwxyz'
                                                                    '23456789')

    ans=sms_login_info(username,pw)# send sms than create db record
    if ans!="ok":
        raise exceptions.ParseError(detail=ans)
    else:
        new_user=User.objects.create_user(username=username,password=pw,nick_name=nick_name)
        new_user.save()
       # new_user.groups.add(Group.objects.get(name=group))
        return new_user

def welcome_renter(renter_phone):
    ans=sms_welcome_renter(renter_phone)# send sms than create db record
    if ans!="ok":
        raise exceptions.ParseError(detail=ans)
    else:
        return True
def verify_phone(phone,code=None):
    if code is not None:
        saved_code=cache.get(phone+'_verify_code')
        if code==saved_code:
            return True
        else:
            return False
    else:
        pw_ls=[]
        for i in range(4):
            pw_ls.append(str(random.randint(0,9)))
        pw="".join(pw_ls)

        ans=sms_verify_code(phone,pw)
        #print(ans.decode('utf-8'))
        if ans=='ok':
            cache.set(phone+'_verify_code',pw,300)
            
        else:
            raise exceptions.ParseError(detail=ans)
        


def get_or_create_user(username,nick_name='',role=None):
    """
    username of model is phone number actually
    """

    pw_ls=[]
    for i in range(4):
        pw_ls.append(str(random.randint(0,9)))
    pw="".join(pw_ls)

    try:
        exist_user=User.objects.get(username=username)
        #sms_login_info(username,"****")
        return exist_user
    except User.DoesNotExist:
        ans=sms_login_info(username,pw)
        if json.loads(ans.decode('utf-8'))["Message"]!="OK":
            raise exceptions.ParseError(detail="failed to create order:phone number not valid")
        else:
            new_user=User.objects.create_user(username=username,password=pw,nick_name=nick_name)
            new_user.role=role
            new_user.save()
            return new_user
