from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'item_no', 'product', 'product_name', 'quantity', 'unit_price', 'amount', 'plan_delivery', 'actual_delivery', 'actual_quantity', 'actual_amount']

class OrderSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'order_no', 'company', 'company_name', 'order_date', 'total_amount', 'items']
