from rest_framework import serializers
from .models import WorkOrder, WorkOrderProcessDetail
from salesmgmt.models import Order
from basedata.models import Product, ProcessCode

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
