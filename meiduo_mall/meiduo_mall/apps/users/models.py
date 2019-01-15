from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from itsdangerous import BadData
from itsdangerous import TimedJSONWebSignatureSerializer


class User(AbstractUser):
    """用户模型类"""
    # mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    mobile = models.CharField(max_length=11, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name="邮箱验证状态")



    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


    def generate_verify_email_url(self):
        """生成激活邮件的url"""
        serializer = TimedJSONWebSignatureSerializer(
            settings.SECRET_KEY,expires_in=60*60*24
        )
        data = {
            'user_id': self.id,
            'email': self.email
        }
        token = serializer.dumps(data).decode()
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        """检查验证邮箱的token"""
        serializer = TimedJSONWebSignatureSerializer(
            settings.SECRET_KEY, expires_in=60 * 60 * 24
        )
        try:
            data = serializer.loads(token)
        except BadData:
            return None

        email = data.get('email')
        user_id = data.get('user_id')
        try:
            return User.objects.get(id=user_id,email=email)
        except User.DoesNotExist:
            return None