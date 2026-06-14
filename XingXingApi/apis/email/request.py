"""
邮件发送 API

POST /api/email/send/

请求体 (application/x-www-form-urlencoded):
    subject=邮件主题&body=邮件正文&recipients=user1@example.com,user2@example.com
"""

import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from XingXingService.email.send_email import send_email_service

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def send_email_view(request):
    """
    发送邮件 API

    请求体 (表单):
        subject (str, 必填):  邮件主题/标题
        body (str, 必填):     邮件正文内容（纯文本）
        recipients (str, 必填): 收件人邮箱，多个以英文逗号分隔
                                  示例: user1@example.com,user2@example.com

    返回:
        成功 200:
        {
            "code": 200,
            "message": "邮件发送完成：成功 2 封，共 2 个收件人",
            "data": {
                "success": true,
                "sent_count": 2,
                "total_count": 2
            }
        }

        失败 400 (参数错误):
        {"code": 400, "message": "邮件主题（subject）不能为空"}

        失败 500 (服务器错误):
        {"code": 500, "message": "邮件发送失败: ..."}
    """
    # ==================== 解析表单参数 ====================
    subject = request.POST.get("subject", "").strip()
    body = request.POST.get("body", "").strip()
    recipients = request.POST.get("recipients", "").strip()

    # ==================== 参数校验 ====================
    if not subject:
        return JsonResponse(
            {"code": 400, "message": "邮件主题（subject）不能为空"},
            status=400,
        )

    if not body:
        return JsonResponse(
            {"code": 400, "message": "邮件正文（body）不能为空"},
            status=400,
        )

    if not recipients:
        return JsonResponse(
            {"code": 400, "message": "收件人列表（recipients）不能为空"},
            status=400,
        )

    # ==================== 发送邮件 ====================
    try:
        result = send_email_service(
            subject=subject,
            body=body,
            recipients=recipients,
        )

        if result["success"]:
            return JsonResponse(
                {
                    "code": 200,
                    "message": result["message"],
                    "data": {
                        "success": True,
                        "sent_count": result["sent_count"],
                        "total_count": result["total_count"],
                    },
                },
                status=200,
            )
        else:
            # 部分成功或全部失败
            return JsonResponse(
                {
                    "code": 500,
                    "message": result["message"],
                    "data": {
                        "success": False,
                        "sent_count": result["sent_count"],
                        "total_count": result["total_count"],
                    },
                },
                status=500,
            )

    except ValueError as e:
        # 参数校验失败（如所有邮箱无效）
        return JsonResponse(
            {"code": 400, "message": str(e)},
            status=400,
        )

    except Exception as e:
        logger.error(f"发送邮件时发生未知错误: {e}", exc_info=True)
        return JsonResponse(
            {"code": 500, "message": f"服务器内部错误: {str(e)}"},
            status=500,
        )
