from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def success_response(data=None, message="成功", status_code=status.HTTP_200_OK):
    """
    标准成功响应格式
    """
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)

def error_response(message="操作失败", code=400, data=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    标准错误响应格式
    """
    return Response({
        "success": False,
        "message": message,
        "code": code,
        "data": data
    }, status=status_code)

def api_exception_handler(exc, context):
    """
    自定义异常处理器
    """
    # 记录异常
    logger.error(f"API异常: {exc}", exc_info=True)
    
    # 处理ValidationError
    if hasattr(exc, 'detail'):
        return error_response(
            message="请求参数错误",
            code=400,
            data=exc.detail,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # 处理其他异常
    return error_response(
        message=str(exc),
        code=500,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

def transaction_atomic_wrapper(view_func):
    """
    事务装饰器，确保视图函数在事务中执行
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        with transaction.atomic():
            return view_func(*args, **kwargs)
    return wrapper

def api_view_exception_handler(view_func):
    """
    API视图异常处理装饰器
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API视图异常: {e}", exc_info=True)
            return error_response(
                message=str(e),
                code=500,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper 