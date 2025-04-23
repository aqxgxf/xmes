from django.db import models
from salesmgmt.models import Order
from base_data.models import Product, ProcessCode, Process, ProcessDetail

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('released', '已下达'),
        ('in_progress', '生产中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    workorder_no = models.CharField(max_length=30, unique=True, verbose_name="工单号")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="订单号")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    remark = models.CharField(max_length=200, blank=True, verbose_name="备注")

    def __str__(self):
        return self.workorder_no

class WorkOrderDetail(models.Model):
    STATUS_CHOICES = [
        ('pending', '待生产'),
        ('in_progress', '生产中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    workorder = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="details", verbose_name="工单号")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="产品")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="数量")
    process_code = models.ForeignKey(ProcessCode, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工艺流程代码")
    plan_start = models.DateTimeField(null=True, blank=True, verbose_name="计划开始时间")
    plan_end = models.DateTimeField(null=True, blank=True, verbose_name="计划结束时间")
    actual_start = models.DateTimeField(null=True, blank=True, verbose_name="实际开始时间")
    actual_end = models.DateTimeField(null=True, blank=True, verbose_name="实际结束时间")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    remark = models.CharField(max_length=200, blank=True, verbose_name="备注")

    def __str__(self):
        return f"{self.workorder.workorder_no} - {self.product.name}"

class WorkOrderProcessDetail(models.Model):
    workorder_detail = models.ForeignKey(WorkOrderDetail, on_delete=models.CASCADE, related_name="process_details", verbose_name="工单明细")
    process_code = models.ForeignKey(ProcessCode, on_delete=models.CASCADE, verbose_name="工艺流程代码")
    step_no = models.PositiveIntegerField(verbose_name="工序号")
    step = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="工序名")
    machine_time = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="设备时间(分钟)")
    labor_time = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="人工时间(分钟)")
    program_file = models.FileField(upload_to='programs/', null=True, blank=True, verbose_name="程序文件")
    status = models.CharField(max_length=20, default='pending', verbose_name="状态")
    actual_start = models.DateTimeField(null=True, blank=True, verbose_name="实际开始时间")
    actual_end = models.DateTimeField(null=True, blank=True, verbose_name="实际结束时间")
    remark = models.CharField(max_length=200, blank=True, verbose_name="备注")

    class Meta:
        unique_together = ("workorder_detail", "step_no")
        verbose_name = '工单工艺明细'
        verbose_name_plural = '工单工艺明细'

    def __str__(self):
        return f"{self.workorder_detail} - 工序{self.step_no}: {self.step.name}"
