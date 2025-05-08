from rest_framework import serializers
from .models import WorkOrder, WorkOrderProcessDetail, ProductionOrder, ProductionMaterial, ProductionLog
from salesmgmt.models import Order
from basedata.models import Product, ProcessCode
from basedata.serializers import ProductSerializer, CustomerSerializer, MaterialSerializer

class WorkOrderProcessDetailSerializer(serializers.ModelSerializer):
    process_name = serializers.CharField(source='process.name', read_only=True)
    process_code = serializers.CharField(source='process.code', read_only=True)
    program_file_url = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderProcessDetail
        fields = ['id', 'workorder', 'step_no', 'process', 'process_name', 'process_code', 
                 'machine_time', 'labor_time', 'plan_start_time', 'plan_end_time', 
                 'actual_start_time', 'actual_end_time', 'pending_quantity', 'processed_quantity',
                 'completed_quantity', 'status', 'remark', 'program_file', 'program_file_url', 'updated_at']
    
    def get_program_file_url(self, obj):
        request = self.context.get('request')
        url = obj.program_file.url if obj.program_file else None
        if url and request and not url.startswith('http'):
            return request.build_absolute_uri(url)
        return url

class WorkOrderSerializer(serializers.ModelSerializer):
    process_details = WorkOrderProcessDetailSerializer(many=True, read_only=True)
    order_no = serializers.SerializerMethodField(read_only=True)
    product_code = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    process_code_text = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = WorkOrder
        fields = ['id', 'workorder_no', 'order', 'order_no', 'product', 'product_code', 
                 'product_name', 'quantity', 'process_code', 'process_code_text', 
                 'plan_start', 'plan_end', 'actual_start', 'actual_end', 'status', 
                 'remark', 'created_at', 'updated_at', 'process_details']
    
    def get_order_no(self, obj):
        if obj.order:
            return obj.order.order_no
        return None
    
    def get_product_code(self, obj):
        if obj.product:
            return obj.product.code
        return None
    
    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        return None
    
    def get_process_code_text(self, obj):
        if obj.process_code:
            return obj.process_code.code
        return None

class ProductionMaterialSerializer(serializers.ModelSerializer):
    """
    生产订单材料序列化器
    """
    material_name = serializers.CharField(source='material.name', read_only=True)
    material_code = serializers.CharField(source='material.code', read_only=True)
    specification = serializers.CharField(source='material.specification', read_only=True)
    
    class Meta:
        model = ProductionMaterial
        fields = [
            'id', 'order', 'material', 'material_name', 'material_code', 
            'specification', 'quantity', 'unit', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductionLogSerializer(serializers.ModelSerializer):
    """
    生产订单日志序列化器
    """
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    
    class Meta:
        model = ProductionLog
        fields = [
            'id', 'order', 'title', 'content', 'log_type',
            'operator', 'operator_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductionOrderSerializer(serializers.ModelSerializer):
    """
    生产订单序列化器
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    
    class Meta:
        model = ProductionOrder
        fields = [
            'id', 'order_number', 'product', 'product_name', 
            'customer', 'customer_name', 'quantity', 'delivery_date',
            'status', 'status_display', 'notes', 
            'creator', 'creator_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']


class ProductionOrderDetailSerializer(ProductionOrderSerializer):
    """
    生产订单详情序列化器，包含材料和日志信息
    """
    materials = ProductionMaterialSerializer(many=True, read_only=True)
    logs = ProductionLogSerializer(many=True, read_only=True)
    product_detail = ProductSerializer(source='product', read_only=True)
    customer_detail = CustomerSerializer(source='customer', read_only=True)
    
    class Meta(ProductionOrderSerializer.Meta):
        fields = ProductionOrderSerializer.Meta.fields + [
            'materials', 'logs', 'product_detail', 'customer_detail'
        ]
