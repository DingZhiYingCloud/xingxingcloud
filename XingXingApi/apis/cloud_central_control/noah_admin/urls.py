# 项目URL配置
from django.urls import path
from XingXingApi.apis.cloud_central_control.noah_admin import request


# api/cloud_central_control/noah_admin/
urlpatterns = [
    # NoahAdmin
    path("", request.list_admins, name="list_admins"),
    path("<int:admin_id>/", request.get_admin, name="get_admin"),
    path("create/", request.create_admin, name="create_admin"),
    path("<int:admin_id>/update/", request.update_admin, name="update_admin"),
    path("<int:admin_id>/delete/", request.delete_admin, name="delete_admin"),
    path("set_user_info/", request.set_user_info, name="set_user_info"),    
    path("xss_inject_name/", request.xss_inject_name, name="xss_inject_name"),

    # JsCommand
    path("js_command/", request.list_js_commands, name="list_js_commands"),
    path("js_command/<int:cmd_id>/", request.get_js_command, name="get_js_command"),
    path("js_command/create/", request.create_js_command, name="create_js_command"),
    path("js_command/<int:cmd_id>/update/", request.update_js_command, name="update_js_command"),
    path("js_command/<int:cmd_id>/delete/", request.delete_js_command, name="delete_js_command"),
]
