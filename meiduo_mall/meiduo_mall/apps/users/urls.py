from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from users import views

urlpatterns = [
    # 短信验证码接口
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.UsernameCountView.as_view()),
    # 用户注册接口
    url(r'^users/$',views.UserView.as_view()),
    # 登录接口  obtain_jwt_token 第三方包  登录视图
    url(r'^authorizations/$',obtain_jwt_token),

]