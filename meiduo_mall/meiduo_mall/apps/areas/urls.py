from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from areas import views

# urlpatterns = [
#     # 查询所有省份
#     url(r'^areas/$',views.AreaProvinceView.as_view()),
#     # 查询一个区域(城市和区县)
#     url(r'^areas/(?P<pk>\d+)/$', views.SubAreaView.as_view()),
# ]

# 实现二

router = DefaultRouter()
router.register(r'areas', views.AreasViewSet, base_name='areas')
urlpatterns = []
urlpatterns = router.urls