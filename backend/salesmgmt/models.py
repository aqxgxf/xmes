from django.db import models
from base_data.models import Company, Product
from django.conf import settings

# Create your models here.

class Order(models.Model):
    order_no = models.CharField(max_length=30, unique=True, verbose_name="订单号")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="公司")
    order_date = models.DateField(verbose_name="下单日期")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="产品", null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="数量")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")
    plan_delivery = models.DateField(verbose_name="计划交货期")
    actual_delivery = models.DateField(null=True, blank=True, verbose_name="实际交货期")
    actual_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="实际交货数量")
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="实际交货金额")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="订单金额合计", default=0)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")

    def __str__(self):
        return self.order_no
