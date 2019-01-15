from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas import serializers
from areas.models import Area
from areas.serializers import AreaSerializer, SubAreaSerializer


# 实现一
# class AreaProvinceView(ListAPIView):
#
#     queryset = Area.objects.filter(parent=None)
#     serializer_class = AreaSerializer
#
# class SubAreaView(RetrieveAPIView):
#
#     queryset = Area.objects.all()
#     serializer_class = SubAreaSerializer


# 实现二
# 为省视图添加缓存CacheResponseMixin
class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    # 如果在配置文件中设置了分页,会影响到此类,
    # 可以设置为None,表示不分页
    pagination_class = None

    def get_queryset(self):
        """提供数据集"""
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        """提供序列化器"""
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer

