# 项目URL配置
from django.urls import path
from XingXingApi.apis.email import request


# api/email/
urlpatterns = [
    path("send/", request.send_email_view, name="send_email"), # 发送邮件
]
