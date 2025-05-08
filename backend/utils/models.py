from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class BaseModel(models.Model):
    """
    所有模型的基类，提供通用字段
    """
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="%(class)s_created", verbose_name="创建人")
    updater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="%(class)s_updated", verbose_name="更新人")
    is_deleted = models.BooleanField("是否删除", default=False)
    deleted_at = models.DateTimeField("删除时间", null=True, blank=True)
    
    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """
        重写删除方法，实现软删除
        """
        hard_delete = kwargs.pop('hard_delete', False)
        if hard_delete:
            return super().delete(*args, **kwargs)
        else:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()

    def hard_delete(self, *args, **kwargs):
        """
        物理删除方法
        """
        return super().delete(*args, **kwargs)

class BaseManager(models.Manager):
    """
    所有模型管理器的基类，提供对软删除的支持
    """
    def get_queryset(self):
        """
        默认只返回未删除的记录
        """
        return super().get_queryset().filter(is_deleted=False)
    
    def all_with_deleted(self):
        """
        返回所有记录，包括已删除的
        """
        return super().get_queryset()
    
    def only_deleted(self):
        """
        只返回已删除的记录
        """
        return super().get_queryset().filter(is_deleted=True) 