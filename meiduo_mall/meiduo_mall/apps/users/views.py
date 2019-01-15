from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

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

class AddressViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    """用户地址管理"""
    serializer_class = serializers.UserAddressSerilaizer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 当前登录用户的地址
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        # 限制返回的地址个数
        count = request.user.addresses.count()
        if count >= 5:
            return Response({'message': '地址个数已达到上限'},status=400)

        return super().create(request, *args, **kwargs)

    # 重写list方法
    def list(self, request, *args, **kwargs):
        """用户地址列表数据"""
        query_set = self.get_queryset()
        serializer = self.get_serializer(query_set,many=True)
        return Response({
            'user_id': request.user.id,
            'default_address_id': request.user.default_address_id,
            'limit': 5,
            'addresses': serializer.data
        })