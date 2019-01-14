from time import sleep

from celery_tasks.main import celery_app


@celery_app.task
def send_sms(mobile, sms_code):
    # CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # print('发送短信验证码:', sms_code)
    sleep(5)
    return sms_code