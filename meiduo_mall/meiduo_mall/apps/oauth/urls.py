from django.conf.urls import url

from oauth import views

urlpatterns = [
    # qq登录接口
    url(r'^qq/authorization/$',views.QQAuthURLView.as_view()),
    # 获取code参数
    url(r'^qq/user/$',views.QQUserView.as_view()),
]