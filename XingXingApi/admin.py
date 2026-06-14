from django.apps import apps
from django.contrib import admin

app_config = apps.get_app_config('XingXingApi')


admin.site.site_header = '星星API'
admin.site.site_title = '星星API管理'

admin.site.site_url = None

for model in app_config.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass