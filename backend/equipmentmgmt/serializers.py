from rest_framework import serializers
from .models import Equipment, EquipmentMaintenance, EquipmentSpare, EquipmentSpareInventory


class EquipmentSerializer(serializers.ModelSerializer):
    """设备序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Equipment
        fields = '__all__'


class EquipmentMaintenanceSerializer(serializers.ModelSerializer):
    """设备维保记录序列化器"""
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = EquipmentMaintenance
        fields = '__all__'


class EquipmentSpareSerializer(serializers.ModelSerializer):
    """设备备件序列化器"""
    current_inventory = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    applicable_equipment_names = serializers.SerializerMethodField()
    
    class Meta:
        model = EquipmentSpare
        fields = '__all__'
    
    def get_applicable_equipment_names(self, obj):
        return [f"{equipment.code} - {equipment.name}" for equipment in obj.applicable_equipment.all()]


class EquipmentSpareInventorySerializer(serializers.ModelSerializer):
    """备件库存记录序列化器"""
    spare_name = serializers.CharField(source='spare.name', read_only=True)
    spare_code = serializers.CharField(source='spare.code', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    related_equipment_name = serializers.CharField(source='related_equipment.name', read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = EquipmentSpareInventory
        fields = '__all__' 