from rest_framework import serializers
from .models import WorkOrder, WorkOrderDetail, WorkOrderProcessDetail

class WorkOrderProcessDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderProcessDetail
        fields = '__all__'

class WorkOrderDetailSerializer(serializers.ModelSerializer):
    process_details = WorkOrderProcessDetailSerializer(many=True, read_only=True)
    class Meta:
        model = WorkOrderDetail
        fields = '__all__'

class WorkOrderSerializer(serializers.ModelSerializer):
    details = WorkOrderDetailSerializer(many=True, read_only=True)
    class Meta:
        model = WorkOrder
        fields = '__all__'
