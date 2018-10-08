from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError

appid = 1400098638
appkey = "cc903c8ebf0874bccf837a8299aae167"
template_id = 133421
ssender = SmsSingleSender(appid, appkey)


def sms_login_info(phone,password):
    try:
        result = ssender.send(0, 86, phone,
                          "用户已创建。账号：{} 密码：{}".format(phone,password))
    except HTTPError as e:
        return "network error"
    code=result['result']
    if code==0:
        return "ok"
    elif code==1016:
        return "phone number not valid"
    elif code == 1026:
        return "please try again later."
    elif code == 1025:
        return "please try again tomorrow."
    else:
        return "unknown error"

def sms_welcome_renter(phone):
    try:
        result = ssender.send(0, 86, phone,
                              "欢迎入住。您可关注我们的公众号，注册用户后在线查询账单。")
    except HTTPError as e:
        return "network error"
    code=result['result']
    if code==0:
        return "ok"
    elif code==1016:
        return "phone number not valid"
    elif code == 1026:
        return "please try again later."
    elif code == 1025:
        return "please try again tomorrow."
    else:
        return "unknown error"

def sms_verify_code(phone,code):
    try:
        result = ssender.send(0, 86, phone,
        "您的验证码为：{}，5分钟内有效。".format(code))
    except HTTPError as e:
        return "network error"
    code=result['result']
    if code==0:
        return "ok"
    elif code==1016:
        return "phone number not valid"
    elif code == 1026:
        return "please try again later."
    elif code == 1025:
        return "please try again tomorrow."
    else:
        return "unknown error"


    

