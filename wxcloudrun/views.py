import json
import logging

from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from wxcloudrun.models import Counters
from wxcloudrun.models import Donation


logger = logging.getLogger('log')


def index(request, _):
    """
    获取主页

     `` request `` 请求对象
    """

    return render(request, 'index.html')

def signup(request,_):
    header=request.headers
    method=request.method
    openid=header.get('X-WX-OPENID')
    data=json.loads(request.body)
    wb_id=data.get('wb_id')
    avatar_url=data.get('avatarUrl')
    nickname=data.get('userInfo')
    amount=data.get('how_much')
    timestamp=data.get('timestamp')

    #create donation
    donation=Donation.objects.create(openid=openid)
    donation.nickname=nickname
    donation.avatar_url=avatar_url
    donation.wb_id=wb_id
    donation.amout=amount
    donation.created_at=timestamp
    
    return JsonResponse({'status': "OK", 'errorMsg': '请求成功', 'openid':openid,'method':method,
                         'wb_id':wb_id,'avatar_url':avatar_url,'nickname':nickname,'amount':amount,'time':timestamp},)
    

def counter(request, _):
    """
    获取当前计数

     `` request `` 请求对象
    """

    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
    if request.method == 'GET' or request.method == 'get':
        rsp = get_count()
    elif request.method == 'POST' or request.method == 'post':
        rsp = update_count(request)
    else:
        rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                            json_dumps_params={'ensure_ascii': False})
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp


def get_count():
    """
    获取当前计数
    """

    try:
        data = Counters.objects.get(id=1)
    except Counters.DoesNotExist:
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    return JsonResponse({'code': 0, 'data': data.count},
                        json_dumps_params={'ensure_ascii': False})


def update_count(request):
    """
    更新计数，自增或者清零

    `` request `` 请求对象
    """

    logger.info('update_count req: {}'.format(request.body))

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    if 'action' not in body:
        return JsonResponse({'code': -1, 'errorMsg': '缺少action参数'},
                            json_dumps_params={'ensure_ascii': False})

    if body['action'] == 'inc':
        try:
            data = Counters.objects.get(id=1)
        except Counters.DoesNotExist:
            data = Counters()
        data.id = 1
        data.count += 1
        data.save()
        return JsonResponse({'code': 0, "data": data.count},
                    json_dumps_params={'ensure_ascii': False})
    elif body['action'] == 'clear':
        try:
            data = Counters.objects.get(id=1)
            data.delete()
        except Counters.DoesNotExist:
            logger.info('record not exist')
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'code': -1, 'errorMsg': 'action参数错误'},
                    json_dumps_params={'ensure_ascii': False})
