"""
文件上传 API

POST /api/upload/

表单参数:
    file (文件, 必填): 要上传的文件

支持的格式:
    图片: jpg, jpeg, png, gif, bmp, webp, svg
    文本: txt
    视频: mp4, avi, mov, wmv, flv, mkv
    压缩包: zip, rar, 7z, tar, gz, bz2

文件大小限制: 100MB
"""

import os
import uuid
import logging
from datetime import datetime

from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    # 图片
    "jpg", "jpeg", "png", "gif", "bmp", "webp", "svg",
    # 文本
    "txt",
    # 视频
    "mp4", "avi", "mov", "wmv", "flv", "mkv",
    # 压缩包
    "zip", "rar", "7z", "tar", "gz", "bz2",
}

# 最大文件大小：100MB
MAX_FILE_SIZE = 100 * 1024 * 1024


def _get_file_extension(filename: str) -> str:
    """获取文件扩展名（小写）"""
    _, ext = os.path.splitext(filename)
    return ext.lstrip(".").lower()


def _generate_filename(original_name: str) -> str:
    """生成唯一文件名，保留原始扩展名"""
    ext = os.path.splitext(original_name)[1]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{timestamp}_{unique_id}{ext}"


@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    """
    POST /api/upload/

    表单参数:
        file (文件, 必填): 上传的文件

    返回:
        成功 200:
        {
            "code": 200,
            "message": "上传成功",
            "data": {
                "url": "/media/uploads/20260614_abc12345.png",
                "file_name": "20260614_abc12345.png",
                "file_size": 123456,
                "original_name": "原始文件名.png"
            }
        }

        失败 400 (参数错误/格式不支持/文件过大):
        {"code": 400, "message": "未选择要上传的文件"}
        {"code": 400, "message": "不支持的文件格式，仅支持: 图片、txt、视频、压缩包"}

        失败 500 (服务器错误):
        {"code": 500, "message": "上传失败: ..."}
    """
    # ==================== 校验文件 ====================
    if "file" not in request.FILES:
        return JsonResponse(
            {"code": 400, "message": "未选择要上传的文件，请使用表单字段名 file"},
            status=400,
        )

    uploaded_file = request.FILES["file"]
    original_name = uploaded_file.name

    # 检查文件大小
    if uploaded_file.size > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE // (1024 * 1024)
        return JsonResponse(
            {"code": 400, "message": f"文件大小超过限制（最大 {max_size_mb}MB）"},
            status=400,
        )

    # 检查文件扩展名
    ext = _get_file_extension(original_name)
    if not ext:
        return JsonResponse(
            {"code": 400, "message": "无法识别文件类型"},
            status=400,
        )
    if ext not in ALLOWED_EXTENSIONS:
        return JsonResponse(
            {
                "code": 400,
                "message": (
                    f"不支持的文件格式 '.{ext}'，"
                    f"仅支持: 图片(jpg/png/gif/bmp/webp/svg)、"
                    f"文本(txt)、视频(mp4/avi/mov/wmv/flv/mkv)、"
                    f"压缩包(zip/rar/7z/tar/gz/bz2)"
                ),
            },
            status=400,
        )

    # ==================== 保存文件 ====================
    try:
        # 确保 uploads 目录存在
        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        new_filename = _generate_filename(original_name)
        save_path = os.path.join(upload_dir, new_filename)

        # 分块写入（大文件友好）
        with open(save_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        file_url = f"{settings.MEDIA_URL}uploads/{new_filename}"

        return JsonResponse(
            {
                "code": 200,
                "message": "上传成功",
                "data": {
                    "url": file_url,
                    "file_name": new_filename,
                    "file_size": uploaded_file.size,
                    "original_name": original_name,
                },
            },
            status=201,
        )

    except Exception as e:
        logger.error(f"文件上传失败: {e}", exc_info=True)
        return JsonResponse(
            {"code": 500, "message": f"上传失败: {str(e)}"},
            status=500,
        )
