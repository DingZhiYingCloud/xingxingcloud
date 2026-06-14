from django.db import models

# 迁移模型
# python manage.py makemigrations
# python manage.py migrate
# xingxingcloud.cloud

class BaseModel(models.Model):
    """项目基础模型，所有业务模型继承此类"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True