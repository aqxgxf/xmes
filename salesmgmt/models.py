from django.db import models
from base_data.models import Company, Product

# Create your models here.

class Order(models.Model):
    order_no = models.CharField(max_length=30, unique=True, verbose_name="订单号")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="公司")
    order_date = models.DateField(verbose_name="下单日期")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="订单金额合计")

    def __str__(self):
        return self.order_no

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="订单号")
    item_no = models.IntegerField(verbose_name="订单项")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="产品")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="数量")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="金额小计")
    plan_delivery = models.DateField(verbose_name="计划交货期")
    actual_delivery = models.DateField(null=True, blank=True, verbose_name="实际交货期")
    actual_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="实际交货数量")
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="实际交货金额")

    def __str__(self):
        return f"{self.order.order_no}-{self.item_no}"
