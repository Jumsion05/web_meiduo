from django.conf.urls import url

from verifications import views

urlpatterns = [
    # 短信验证码路由
    url(r'^sms_codes/(1[35678]\d{9})/$',views.SMSCodeView.as_view())
]