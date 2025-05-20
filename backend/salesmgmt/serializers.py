from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)  # 自动补全公司名称
    order_number = serializers.CharField(source='order_no', read_only=True)  # 自动补全订单号

    def validate_order_no(self, value):
        # 校验订单号唯一性（不区分大小写）
        qs = Order.objects.filter(order_no__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("订单号已存在（不区分大小写）")
        return value
    class Meta:
        model = Order
        fields = '__all__'
