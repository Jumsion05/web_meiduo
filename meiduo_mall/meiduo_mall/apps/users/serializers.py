import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from celery_tasks.email.tasks import send_verify_email
from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label="确认密码", write_only=True)
    sms_code = serializers.CharField(label="短信验证码", write_only=True)
    allow = serializers.BooleanField(label="同意协议", write_only=True)
    #  注册成功自动登录，需要生成jwt并返回给客户端
    token = serializers.CharField(label="登录状态Token", read_only=True)

    def create(self, validated_data):
        """创建一个用户对象"""

        user = User.objects.create_user(
            username=validated_data.get("username"),
            password=validated_data.get("password"),
            mobile=validated_data.get("mobile"),
        )

        # todo  生成jwt
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 生成payload的方法
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 生成ｊｗｔ方法

        payload = jwt_payload_handler(user)  # 生成payload ，字典
        token = jwt_encode_handler(payload)  # 生成jwt 字符串
        user.token = token  # 生成的jwt序列化返回

        return user

    def validate_mobile(self, value):
        """验证手机号"""

        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')

        return value

    def validate_allow(self, value):
        """检验用户是否同意协议"""

        if not value:
            raise serializers.ValidationError('请同意用户协议')

        return value

    def validate(self, attrs):
        # 判断两次密码
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码
        # redis_conn = get_redis_connection('sms_codes')
        # mobile = attrs['mobile']
        # real_sms_code = redis_conn.get('sms_%s' % mobile)
        #
        # if real_sms_code is None:
        #     raise serializers.ValidationError('无效的短信验证码')
        #
        # if attrs['sms_code'] != real_sms_code.decode():
        #     raise serializers.ValidationError('短信验证码错误')

        return attrs

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2',
                  'sms_code', 'mobile', 'allow', 'token')  # 添加token

        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情页信息序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')

class EmailSerilaizer(serializers.ModelSerializer):
    """修改用户邮箱序列化器"""
    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        email = validated_data['email']
        instance.email = email
        instance.save()

        # 生成并发送激活邮件
        verify_url = instance.generate_verify_email_url()
        print(verify_url)
        send_verify_email.delay(email, verify_url)
        print("----1--------")

        return instance