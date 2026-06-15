# 项目URL配置
from django.urls import path, include


# api/
urlpatterns = [
    path('email/', include('XingXingApi.apis.email.urls')), # 邮箱接口
    path('cloud_central_control/', include('XingXingApi.apis.cloud_central_control.urls')), # 云控接口
    path('upload/', include('XingXingApi.apis.upload.urls')), # 文件上传接口
]
