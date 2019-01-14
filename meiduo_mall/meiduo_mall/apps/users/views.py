from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
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