from django.db import models
from salesmgmt.models import Order
from basedata.models import Product, ProcessCode, Process, ProcessDetail

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
