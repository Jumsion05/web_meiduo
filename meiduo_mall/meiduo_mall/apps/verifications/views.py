from time import sleep

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from redis import StrictRedis
from rest_framework.response import Response
from rest_framework.views import APIView

from celery_tasks.sms.tasks import send_sms
from meiduo_mall.utils.exceptions import logger


class SMSCodeView(APIView):

    def get(self,request,mobile):
        # 获取StrictRedis保存数据
        strict_redis = get_redis_connection("sms_codes") #type: StrictRedis
        # 4. 60秒之内禁止重复发送验证码
        sms_flag = strict_redis.get("sms_flag_%s"%mobile)
        if sms_flag:
            return Response({"message":"发送短信过于频繁"},status=400)

        # 1.生成短信验证码
        import random
        sms_code = "%06d" %random.randint(0,999999)
        logger.info('sms_code: %s'%sms_code)
        # 2.使用云通讯发送短信
        # CCP().send_template_sms(mobile, [sms, 5], 1)
        # sleep(5)
        # 使用celery发送耗时验证码
        send_sms.delay(mobile,sms_code)
        print(sms_code)
        # 3.保存短信验证码到redis中
        strict_redis.setex("sms_%s"%mobile,5*60,sms_code)
        strict_redis.setex("sms_flag_%s"%mobile,60,1)

        return Response({"message":"OK"})
