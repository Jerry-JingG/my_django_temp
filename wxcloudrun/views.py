import json
import logging

from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from wxcloudrun.models import Counters
from wxcloudrun.models import Donation
from wxcloudrun.recog_bill import recog_bill
import os
import requests


logger = logging.getLogger('log')

def get(request,_):
    # 1. 获取 cloudid 参数
    data=json.loads(request.body)
    cloudid = data.get("fileid")
    if not cloudid:
        return JsonResponse({"error": "没有要下载的文件"}, status=400)

    # 2. 设置环境ID
    envid = os.getenv("CBR_ENV_ID", "werun-id")

    # 3. 准备请求参数
    param = {
        "env": envid,
        "file_list": [
            {
                "fileid": cloudid,
                "max_age": 86400  # 设置最大缓存时间为1天
            }
        ]
    }

    # 4. 使用 requests 库调用微信 API
    try:
        response = requests.post(
            url="https://api.weixin.qq.com/tcb/batchdownloadfile",
            headers={"Content-Type": "application/json"},
            data=json.dumps(param)
        )
        response.raise_for_status()  # 检查请求是否成功
        file_list = response.json().get("file_list", [])
        if not file_list or file_list[0].get("status") != 0:
            return JsonResponse({"error": "文件下载链接获取失败"}, status=400)

        download_url = file_list[0].get("download_url")
        
        # 5. 下载图片
        img_response = requests.get(download_url)
        img_response.raise_for_status()

        # 6. 将图片转为 PIL Image 对象
        bill=recog_bill(img_response)
        message_dict=bill.distill_from_bill()

        # 8. 返回识别结果
        return JsonResponse(message_dict)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
    #     return JsonResponse(response.json())  # 返回微信 API 的响应内容
    # except requests.exceptions.RequestException as e:
    #     return JsonResponse({"error": str(e)}, status=500)
    


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
    donation = Donation(
    openid=openid,
    nickname=nickname,
    avatar_url=avatar_url,
    wb_id=wb_id,
    amount=amount,
    created_at=timestamp
    )
    donation.save()

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
