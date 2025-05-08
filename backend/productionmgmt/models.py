from django.db import models
from salesmgmt.models import Order
from basedata.models import Product, ProcessCode, Process, ProcessDetail, Customer, Material
from utils.models import BaseModel, BaseManager
from django.contrib.auth.models import User

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('print', '待打印'),
        ('released', '已下达'),
        ('in_progress', '生产中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    workorder_no = models.CharField(max_length=30, unique=True, verbose_name="工单号")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="订单号")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="产品", null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="数量")
    process_code = models.ForeignKey(ProcessCode, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工艺流程代码")
    plan_start = models.DateTimeField(null=True, blank=True, verbose_name="计划开始时间")
    plan_end = models.DateTimeField(null=True, blank=True, verbose_name="计划结束时间")
    actual_start = models.DateTimeField(null=True, blank=True, verbose_name="实际开始时间")
    actual_end = models.DateTimeField(null=True, blank=True, verbose_name="实际结束时间")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="状态")
    remark = models.CharField(max_length=200, blank=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.workorder_no

class WorkOrderProcessDetail(models.Model):
    STATUS_CHOICES = [
        ('pending', '待生产'),
        ('in_progress', '生产中'),
        ('completed', '已完成'),
        ('skipped', '已跳过'),
    ]
    workorder = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='process_details', verbose_name="工单")
    step_no = models.PositiveIntegerField(verbose_name="工序号")
    process = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="工序")
    machine_time = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="设备时间(分钟)")
    labor_time = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="人工时间(分钟)")
    plan_start_time = models.DateTimeField(null=True, blank=True, verbose_name="计划开始时间")
    plan_end_time = models.DateTimeField(null=True, blank=True, verbose_name="计划结束时间")
    actual_start_time = models.DateTimeField(null=True, blank=True, verbose_name="实际开始时间")
    actual_end_time = models.DateTimeField(null=True, blank=True, verbose_name="实际结束时间")
    pending_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="待加工数量")
    processed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="已加工数量")
    completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="完工数量")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    remark = models.CharField(max_length=200, blank=True, verbose_name="备注")
    program_file = models.FileField(upload_to='workorder_programs/', null=True, blank=True, verbose_name="程序文件")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        unique_together = ("workorder", "step_no")
        ordering = ["workorder", "step_no"]
        verbose_name = '工单工艺明细'
        verbose_name_plural = '工单工艺明细'

    def __str__(self):
        return f"{self.workorder.workorder_no} - 工序{self.step_no}: {self.process.name}"

class ProductionOrderManager(BaseManager):
    """
    生产订单管理器，提供对软删除的支持
    """
    pass

class ProductionOrder(BaseModel):
    """
    生产订单模型
    """
    ORDER_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('planned', '已计划'),
        ('in_progress', '生产中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    # 基本信息
    order_number = models.CharField("订单编号", max_length=30, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="产品")
    customer = models.ForeignKey('basedata.Customer', on_delete=models.PROTECT, verbose_name="客户")
    quantity = models.PositiveIntegerField("数量")
    delivery_date = models.DateField("交付日期")
    status = models.CharField("状态", max_length=20, choices=ORDER_STATUS_CHOICES, default='draft')
    notes = models.TextField("备注", blank=True, null=True)
    
    # 使用自定义管理器
    objects = ProductionOrderManager()
    
    class Meta:
        verbose_name = "生产订单"
        verbose_name_plural = "生产订单"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.product.name} ({self.get_status_display()})"


class ProductionMaterial(BaseModel):
    """
    生产订单材料清单
    """
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='materials', verbose_name="生产订单")
    material = models.ForeignKey('basedata.Material', on_delete=models.PROTECT, verbose_name="材料")
    quantity = models.DecimalField("数量", max_digits=10, decimal_places=2)
    unit = models.CharField("单位", max_length=20)
    notes = models.TextField("备注", blank=True, null=True)
    
    class Meta:
        verbose_name = "订单材料"
        verbose_name_plural = "订单材料"
        
    def __str__(self):
        return f"{self.material.name} - {self.quantity} {self.unit}"


class ProductionLog(BaseModel):
    """
    生产订单日志记录
    """
    LOG_TYPE_CHOICES = [
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('success', '成功'),
    ]
    
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='logs', verbose_name="生产订单")
    title = models.CharField("标题", max_length=100)
    content = models.TextField("内容")
    log_type = models.CharField("类型", max_length=20, choices=LOG_TYPE_CHOICES, default='info')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="操作人")
    
    class Meta:
        verbose_name = "生产日志"
        verbose_name_plural = "生产日志"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
