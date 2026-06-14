# 项目URL配置
from django.urls import path, include


# api/cloud_central_control/
urlpatterns = [
    path('noah_admin/', include('XingXingApi.apis.cloud_central_control.noah_admin.urls')),
]
