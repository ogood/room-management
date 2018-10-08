from django.urls import reverse
import json
#import requests
from apps.helpers.sms.send import sms_login_info
#python manage.py shell < tests.py
#print(reverse('dashboard:child-product-detail',kwargs={'parent_pk':1,'pk':1}))
print(reverse('product:region-list'))
#print(sms_login_info("15618232902","123mm"))

'''
url='http://host.com:8000/api-login/'
url2='http://host.com:8000/manage/product/'
data = {'username': 'admin','password':'admin'}
headers = {'Accept': 'application/json',
"Accept-Language": "en-US",
"Authorization":"Token 0f35af8bb23c0a8e4285645128e84f5e313f8284",
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

r = requests.get(url2,  headers=headers)

print(r.text)
'''
exit()