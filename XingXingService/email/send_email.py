"""
邮件发送服务

提供 send_email_service 函数，用于发送单封或多封邮件。
"""

import logging
from typing import Optional

from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email, ValidationError

logger = logging.getLogger(__name__)


def send_email_service(
    subject: str,
    body: str,
    recipients: str,
    from_email: Optional[str] = None,
    fail_silently: bool = False,
) -> dict:
    """
    发送邮件服务（支持单发和批量发送）

    参数:
        subject: 邮件主题/标题（必填）
        body: 邮件正文内容（必填，纯文本格式）
        recipients: 收件人列表（必填），多个收件人以英文逗号分隔
                    示例: "user1@example.com,user2@example.com"
        from_email: 发件人地址（可选，默认使用 settings.DEFAULT_FROM_EMAIL）
        fail_silently: 发送失败时是否静默处理（可选，默认 False）

    返回:
        dict: 包含发送结果的字典
            {
                "success": bool,          # 是否全部发送成功
                "sent_count": int,        # 成功发送数量
                "total_count": int,       # 总收件人数
                "message": str,           # 结果描述
                "errors": [str],          # 错误列表（仅在出错时包含）
                "invalid_emails": [str],  # 无效邮箱列表（仅在存在无效邮箱时包含）
            }

    异常:
        以下情况抛出 ValueError:
            - subject 为空
            - body 为空
            - recipients 为空
            - 所有收件人邮箱均无效

    使用示例:
        # 基本用法
        result = send_email_service(
            subject="系统通知",
            body="您的账户已创建成功。",
            recipients="user@example.com"
        )

        # 批量发送
        result = send_email_service(
            subject="批量通知",
            body="这是一封批量通知邮件。",
            recipients="user1@example.com,user2@example.com,user3@example.com"
        )

        # 指定发件人
        result = send_email_service(
            subject="测试",
            body="测试内容",
            recipients="user@example.com",
            from_email="noreply@example.com"
        )
    """
    # ==================== 参数校验 ====================
    if not subject or not subject.strip():
        raise ValueError("邮件主题（subject）不能为空")

    if not body or not body.strip():
        raise ValueError("邮件正文（body）不能为空")

    if not recipients or not recipients.strip():
        raise ValueError("收件人列表（recipients）不能为空")

    # ==================== 解析收件人 ====================
    # 按英文逗号分割，并去除每个邮箱的前后空格
    recipient_list = [email.strip() for email in recipients.split(",") if email.strip()]

    if not recipient_list:
        raise ValueError("收件人列表（recipients）中未包含有效的邮箱地址")

    # ==================== 校验邮箱格式 ====================
    valid_emails = []
    invalid_emails = []

    for email in recipient_list:
        try:
            validate_email(email)
            valid_emails.append(email)
        except ValidationError:
            invalid_emails.append(email)

    if not valid_emails:
        raise ValueError(
            f"所有收件人邮箱均无效，无效邮箱列表: {', '.join(invalid_emails)}"
        )

    # ==================== 设置发件人 ====================
    sender = from_email or settings.DEFAULT_FROM_EMAIL
    if not sender:
        raise ValueError(
            "发件人地址未配置，请在 .env 中设置 EMAIL_HOST_USER，"
            "或在调用时传入 from_email 参数"
        )

    # ==================== 发送邮件 ====================
    try:
        sent_count = send_mail(
            subject=subject.strip(),
            message=body.strip(),
            from_email=sender,
            recipient_list=valid_emails,
            fail_silently=fail_silently,
        )

        # Django 的 send_mail() 发给 N 个收件人时返回 1（一封邮件）
        # 只要成功发送即视为成功
        success = sent_count > 0

        result = {
            "success": success,
            "sent_count": sent_count,
            "total_count": len(recipient_list),
            "message": (
                f"邮件发送成功，共 {len(recipient_list)} 个收件人"
                if success
                else "邮件发送失败"
            ),
        }

        if invalid_emails:
            result["invalid_emails"] = invalid_emails
            result["message"] += f"，{len(invalid_emails)} 个邮箱格式无效已跳过"

        logger.info(result["message"])
        return result

    except Exception as e:
        error_msg = f"邮件发送失败: {str(e)}"
        logger.error(error_msg, exc_info=True)

        result = {
            "success": False,
            "sent_count": 0,
            "total_count": len(recipient_list),
            "message": error_msg,
            "errors": [str(e)],
        }

        if invalid_emails:
            result["invalid_emails"] = invalid_emails

        return result
