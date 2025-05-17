from rest_framework import serializers
from .models import WorkOrder, WorkOrderProcessDetail, WorkOrderFeedback
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
                 'machine_time', 'labor_time', 'process_content', 'plan_start_time', 'plan_end_time',
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

class WorkOrderFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderFeedback
        fields = [
            'id', 'workorder_process', 'completed_quantity', 'defective_quantity',
            'defective_reason', 'remark', 'created_by', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']

class WorkOrderFeedbackCreateSerializer(serializers.Serializer):
    workorder_process_id = serializers.IntegerField()
    completed_quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    defective_quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    defective_reason = serializers.CharField(required=False, allow_blank=True)
    remark = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        验证总数量不超过待加工数量，并且不良品有原因
        """
        completed = data.get('completed_quantity', 0)
        defective = data.get('defective_quantity', 0)
        total = completed + defective
        
        if total <= 0:
            raise serializers.ValidationError("完成数量和不良品数量总和必须大于0")
        
        # 检查工序是否存在
        try:
            workorder_process = WorkOrderProcessDetail.objects.get(
                pk=data['workorder_process_id']
            )
        except WorkOrderProcessDetail.DoesNotExist:
            raise serializers.ValidationError("工序不存在")
            
        # 检查数量是否超过
        if total > workorder_process.pending_quantity:
            raise serializers.ValidationError(
                f"总数量不能超过待加工数量({workorder_process.pending_quantity})"
            )
            
        # 检查不良品原因
        if defective > 0 and not data.get('defective_reason'):
            raise serializers.ValidationError("存在不良品时必须填写不良原因")
            
        return data

