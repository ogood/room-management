# -*- coding: utf-8 -*-
import sys
from .aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from .aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest
from aliyunsdkcore.client import AcsClient
import uuid
from aliyunsdkcore.profile import region_provider
from aliyunsdkcore.http import method_type as MT
from aliyunsdkcore.http import format_type as FT
from django.conf import settings

"""
短信业务调用接口示例，版本号：v20170525

Created on 2017-06-12

"""

# 注意：不要更改
REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"

acs_client = AcsClient(settings.SMS["ACCESS_KEY_ID"], settings.SMS["ACCESS_KEY_SECRET"], REGION)
region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)

def send_sms(business_id, phone_numbers, sign_name, template_code, template_param=None):
    smsRequest = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)

    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)

    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)

    # 短信签名
    smsRequest.set_SignName(sign_name)
	
    # 数据提交方式
	# smsRequest.set_method(MT.POST)
	
	# 数据提交格式
    # smsRequest.set_accept_format(FT.JSON)
	
    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)

    # TODO 业务处理

    return smsResponse

def sms_login_info(phone,password):
    params = "{\"phone\":\"%s\",\"password\":\"%s\"}" % (phone,password)
    #params = u'{"name":"wqb","code":"12345678","address":"bz","phone":"13000000000"}'
    return send_sms(uuid.uuid1(), phone, "胡越古", "SMS_136381649", params)

def sms_welcome_renter(phone):
    #params = "{\"phone\":\"%s\",\"password\":\"%s\"}" % phone
    #params = u'{"name":"wqb","code":"12345678","address":"bz","phone":"13000000000"}'
    return send_sms(uuid.uuid1(), phone, "胡越古", "SMS_136381892")

def sms_verify_code(phone,code):
    params = "{\"phone\":\"%s\",\"code\":\"%s\"}" % (phone,code)
    #params = u'{"name":"wqb","code":"12345678","address":"bz","phone":"13000000000"}'
    return send_sms(uuid.uuid1(), phone, "胡越古", "SMS_136388476",params)

if __name__ == '__main__':
    __business_id = uuid.uuid1()
    #print(__business_id)
    #params = "{\"password\":\"eddd2\"}"
	#params = u'{"name":"wqb","code":"12345678","address":"bz","phone":"13000000000"}'
    #print(send_sms(__business_id, "15618232902", "胡越古", "SMS_130845450", params))
    
    

