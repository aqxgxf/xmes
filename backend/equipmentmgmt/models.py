from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Equipment(models.Model):
    """设备模型：存储设备的基本信息"""
    
    # 设备状态选项
    STATUS_CHOICES = (
        ('normal', '正常'),
        ('maintenance', '维修中'),
        ('inspection', '待检'),
        ('disabled', '停用'),
    )
    
    code = models.CharField(max_length=50, unique=True, verbose_name='设备编号')
    name = models.CharField(max_length=100, verbose_name='设备名称')
    model = models.CharField(max_length=100, verbose_name='设备型号')
    specification = models.TextField(blank=True, null=True, verbose_name='规格参数')
    manufacturer = models.CharField(max_length=100, blank=True, null=True, verbose_name='生产厂商')
    purchase_date = models.DateField(blank=True, null=True, verbose_name='购买日期')
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='购买价格')
    installation_date = models.DateField(blank=True, null=True, verbose_name='安装日期')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='设备位置')
    responsible_person = models.CharField(max_length=50, blank=True, null=True, verbose_name='负责人')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='normal', verbose_name='设备状态')
    next_maintenance_date = models.DateField(blank=True, null=True, verbose_name='下次维保日期')
    image = models.ImageField(upload_to='equipment/', blank=True, null=True, verbose_name='设备图片')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '设备'
        verbose_name_plural = '设备'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class EquipmentMaintenance(models.Model):
    """设备维保记录模型：记录设备的维保历史"""
    
    # 维保类型选项
    TYPE_CHOICES = (
        ('routine', '例行保养'),
        ('repair', '故障维修'),
        ('inspection', '定期检查'),
        ('calibration', '校准'),
    )
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_records', verbose_name='设备')
    maintenance_date = models.DateField(verbose_name='维保日期')
    maintenance_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='维保类型')
    description = models.TextField(verbose_name='维保内容')
    performed_by = models.CharField(max_length=50, verbose_name='执行人')
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='维保费用')
    result = models.TextField(blank=True, null=True, verbose_name='维保结果')
    next_maintenance_date = models.DateField(blank=True, null=True, verbose_name='下次维保日期')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_maintenances', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '设备维保记录'
        verbose_name_plural = '设备维保记录'
        ordering = ['-maintenance_date']
    
    def __str__(self):
        return f"{self.equipment.name} - {self.maintenance_date} - {self.get_maintenance_type_display()}"
    
    def save(self, *args, **kwargs):
        # 如果设置了下次维保日期，自动更新设备的下次维保日期
        if self.next_maintenance_date and self.equipment:
            self.equipment.next_maintenance_date = self.next_maintenance_date
            self.equipment.save(update_fields=['next_maintenance_date'])
        super().save(*args, **kwargs)


class EquipmentSpare(models.Model):
    """设备备件模型：管理与设备相关的备件信息"""
    
    code = models.CharField(max_length=50, unique=True, verbose_name='备件编号')
    name = models.CharField(max_length=100, verbose_name='备件名称')
    model = models.CharField(max_length=100, verbose_name='备件型号')
    specification = models.TextField(blank=True, null=True, verbose_name='规格参数')
    manufacturer = models.CharField(max_length=100, blank=True, null=True, verbose_name='生产厂商')
    unit = models.CharField(max_length=20, blank=True, null=True, verbose_name='单位')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='单价')
    min_inventory = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='最小库存')
    applicable_equipment = models.ManyToManyField(Equipment, related_name='applicable_spares', blank=True, verbose_name='适用设备')
    image = models.ImageField(upload_to='equipment_spares/', blank=True, null=True, verbose_name='备件图片')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '设备备件'
        verbose_name_plural = '设备备件'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def current_inventory(self):
        """获取当前库存数量"""
        from django.db.models import Sum
        total = self.inventory_records.aggregate(Sum('quantity'))['quantity__sum'] or 0
        return total


class EquipmentSpareInventory(models.Model):
    """备件库存变动记录模型：记录备件的入库、出库历史"""
    
    # 变动类型选项
    TYPE_CHOICES = (
        ('in', '入库'),
        ('out', '出库'),
    )
    
    spare = models.ForeignKey(EquipmentSpare, on_delete=models.CASCADE, related_name='inventory_records', verbose_name='备件')
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='变动类型')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='数量')
    transaction_date = models.DateTimeField(default=timezone.now, verbose_name='变动日期')
    related_equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, related_name='spare_usages', verbose_name='相关设备')
    related_maintenance = models.ForeignKey(EquipmentMaintenance, on_delete=models.SET_NULL, null=True, blank=True, related_name='spare_usages', verbose_name='相关维保记录')
    batch_no = models.CharField(max_length=50, blank=True, null=True, verbose_name='批次号')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='spare_inventory_records', verbose_name='操作人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '备件库存记录'
        verbose_name_plural = '备件库存记录'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.spare.name} - {self.get_transaction_type_display()} - {self.quantity}" 