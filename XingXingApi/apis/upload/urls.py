# 项目URL配置
from django.urls import path
from XingXingApi.apis.upload import request


# api/upload/
urlpatterns = [
    path("", request.upload_file, name="upload_file"), # 文件上传
]
