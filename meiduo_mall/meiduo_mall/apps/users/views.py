from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users import serializers
from users.models import User
from users.serializers import CreateUserSerializer


class UsernameCountView(APIView):
    """用户是否已存在"""
    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        data = {
            "username": username,
            "count": count
        }
        return Response(data)

class UserView(CreateAPIView):
    """用户注册"""
    serializer_class = CreateUserSerializer

class UserDetailView(RetrieveAPIView):
    """用户详情"""
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

class EmailView(UpdateAPIView):
    """保存邮箱"""
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.EmailSerilaizer

    def get_object(self):
        return self.request.user

class VerifyEmailView(APIView):
    """激活邮件"""
    def get(self,request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=400)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'})
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})