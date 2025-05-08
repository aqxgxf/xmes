from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

class IsAdminUser(BasePermission):
    """
    仅允许管理员用户访问
    """
    message = _('仅管理员可以执行此操作。')

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff
        )

class IsSuperUser(BasePermission):
    """
    仅允许超级管理员访问
    """
    message = _('仅超级管理员可以执行此操作。')

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_superuser
        )

class IsInGroup(BasePermission):
    """
    检查用户是否在指定的组中
    """
    message = _('您没有权限执行此操作。')

    def __init__(self, group_name):
        self.group_name = group_name

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name=self.group_name).exists()

class IsOwnerOrReadOnly(BasePermission):
    """
    仅允许对象的创建者编辑或删除对象
    """
    message = _('您只能编辑或删除自己创建的内容。')

    def has_object_permission(self, request, view, obj):
        # 允许所有人查看
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # 只允许创建者修改或删除
        return obj.creator == request.user

def get_tokens_for_user(user):
    """
    获取用户的 JWT token
    """
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_user_from_token(token):
    """
    从 token 获取用户
    """
    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        return user
    except Exception:
        return None 