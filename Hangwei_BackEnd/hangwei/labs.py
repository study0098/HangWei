from django.http import HttpResponse
from django.conf import settings
import json
from .models import *
import urllib.request
import requests
import base64
import os
import datetime, time
from django.db.models import Avg, Q, F, Sum
from django.core import serializers
import random
from django.core.cache import cache
import redis
from PIL import Image
from io import BytesIO


def get_access_token():
    """
    get access token from baidu api
    :return:
    """
    api_key = 'cu9ovD9BFtagVdsZX5FdDStX'
    secret_key = 'dwLG00qWpfYcYPKFoiH1oCMXIqHuQmTA'
    url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' \
          + str(api_key) + '&client_secret=' + str(secret_key)
    res = requests.get(url).text
    a = eval(res)
    access_token = a['access_token']
    return access_token


def lab_identify_dish(request):
    """
    identify dish by baidu api
    :param request:
    :return:
    """
    # 本地测试版
    # img_url = 'img/10/0a587eef41.jpg'
    # f = open(os.path.abspath('.') + '/media/' + img_url, 'rb')
    # image = base64.b64encode(f.read())
    url = 'https://aip.baidubce.com/rest/2.0/image-classify/v2/dish?access_token=' + str(get_access_token())
    header = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    img = request.FILES['img']
    img = Image.open(img)       # 读取为PIL 图像格式

    output_buffer = BytesIO()   # 转化为Base64编码
    img.save(output_buffer, format='JPEG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)

    data = dict()
    data['image'] = str(base64_str, 'utf-8')

    res = requests.post(url=url, data=data, headers=header).text
    json_data = json.loads(res)
    return HttpResponse(json.dumps(json_data['result']), content_type='application/json', charset='utf-8')
