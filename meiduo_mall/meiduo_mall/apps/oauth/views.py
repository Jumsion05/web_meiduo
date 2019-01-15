from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthQQUser
from oauth.serializers import QQUserSerializer
from oauth.utils import generate_encrypted_openid


class QQAuthURLView(APIView):
    """
    提供QQ登录页面网址
    """
    def get(self,request):
        # next表示从哪个页面进入到的登录页面,将来登录成功后就自动回到那个页面
        next = request.query_params.get("next")
        if not next:
            next = "/" # 首页

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)

        login_url = oauth.get_qq_url()
        return Response({"login_url": login_url})


class QQUserView(APIView):
    """用户扫码登录的回调函数"""

    def get(self,request):
        # 提取code请求参数
        code = request.query_params.get("code")
        print(code)
        if not code:
            return Response({"message": "缺少code"},status=400)

        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            # 使用code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)
            # 通过access_token向QQ服务器获取openid
            openid = oauth.get_open_id(access_token)
            print("openid:", openid)
            # return Response({"openid":openid})
        except:
            return Response({"message": "QQ服务器异常"}, status=503)

        # 使用openid查询该QQ用户是否在美多商城中绑定用户
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
            print(oauth_user)
        except OAuthQQUser.DoesNotExist:
            # 如果openid没有绑定美多商城用户,则需要进行绑定

            # 在这里将openid返回给前端,绑定再传给服务器(加密签名后再响应给客户端)
            openid = generate_encrypted_openid(openid)
            return Response({"openid": openid})
        else:
            # 到此表示登录成功,如果openid已经绑定美多用户,直接生成JWT token,并返回
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            # 获取oauth_user关联的user
            user = oauth_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                "token": token,
                "user_id": user.id,
                "username": user.username
            })
            return response

    def post(self,request):
        """
        绑定openid和美多用户
        """
        # 创建序列化器对象
        serializer = QQUserSerializer(data=request.data)
        # 校验请求参数
        serializer.is_valid()
        # 绑定openid和美多用户
        user = serializer.save()

        # 到此为止,绑定成功
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        response = Response({
            "token": token,
            "user_id": user.id,
            "username": user.username
        })
        return response