from django.db import models

from XingXingApi.models.base import BaseModel


class NoahAdmin(BaseModel):
    """管理员账号模型"""

    account = models.CharField(max_length=100, unique=True, verbose_name='账号')
    password = models.CharField(max_length=255, verbose_name='密码')
    email = models.EmailField(max_length=255, blank=True, default='', verbose_name='邮箱')
    cookie = models.TextField(blank=True, default='', verbose_name='Cookie')

    class Meta:
        db_table = 'noah_admin'
        verbose_name = '管理员账号'
        verbose_name_plural = '管理员账号'

    def __str__(self):
        return self.account


class JsCommand(BaseModel):
    """JS 命令模型 - 记录需要执行的 JS 代码"""

    name = models.CharField(max_length=200, unique=True, verbose_name='命令名称')
    js_code_url = models.CharField(max_length=500, verbose_name='JS代码完整URL路径')
    is_required = models.BooleanField(default=True, verbose_name='是否需要执行')

    class Meta:
        db_table = 'noah_admin_js_command'
        verbose_name = 'noah_admin_JS命令'
        verbose_name_plural = 'noah_admin_JS命令'

    def __str__(self):
        return self.name
