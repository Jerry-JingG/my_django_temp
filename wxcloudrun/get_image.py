import os
import requests
from django.http import JsonResponse
from django.http import HttpResponse
import json

def get(cloudid):
    # 1. 获取 cloudid 参数
    # data=json.loads(request.body)
    # cloudid = data.get("fileid")
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
        return JsonResponse(response.json())  # 返回微信 API 的响应内容
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

json_re=get("cloud://prod-7gh8xx1o7d00c9a2.7072-prod-7gh8xx1o7d00c9a2-1328894167/image/WechatIMG302.jpg")
print(json_re)