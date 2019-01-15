from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.models import OAuthQQUser
from oauth.utils import check_encrypted_openid
from users.models import User


class QQUserSerializer(serializers.Serializer):
    """QQ登录创建用户序列化器"""
    openid = serializers.CharField(label='openid', write_only=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$',
                                    write_only=True)
    password = serializers.CharField(label='密码', max_length=20, min_length=8,
    write_only = True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)

    def validate(self, attrs):

        # 获取openid,校验openid
        encrypted_openid = attrs['openid']
        openid = check_encrypted_openid(encrypted_openid)
        if not openid:
            raise serializers.ValidationError('无效的openid')

        # 修改字典中openid的值,以保证正确的openid到映射表
        attrs['openid'] = openid

        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        password = attrs['password']

        # 校验短信验证码
        redis_conn = get_redis_connection('sms_codes')
        real_sms_code = redis_conn.get('sms_%s'%mobile)
        if not  real_sms_code:
            raise serializers.ValidationError('短信验证码无效')

        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        try: # 查询要绑定的用户,如果存在,校验密码是否正确
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 用户保存在,则自定新增一个美多用户进行绑定
            user = User.objects.create_user(
                username = mobile,
                password = password,
                mobile = mobile
            )
        if not user.check_password(password):
            raise serializers.ValidationError('密码错误')

        # 将认证后的user放进校验字典中, 绑定关联时用到
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        # 获取校验的用户
        user = validated_data.get('user')
        openid = validated_data.get('openid')

        # 绑定openid和美多用户, 新增一条表数据
        OAuthQQUser.objects.create(
            openid = openid,
            user = user
        )
        return user  # 返回美多用户
