from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from .models import Equipment, EquipmentMaintenance, EquipmentSpare, EquipmentSpareInventory
from .serializers import (
    EquipmentSerializer, 
    EquipmentMaintenanceSerializer, 
    EquipmentSpareSerializer, 
    EquipmentSpareInventorySerializer
)


class EquipmentViewSet(viewsets.ModelViewSet):
    """设备视图集"""
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['code', 'name', 'model', 'manufacturer', 'location', 'responsible_person']
    filterset_fields = ['status']

    @action(detail=True, methods=['get'])
    def maintenance_records(self, request, pk=None):
        """获取设备的维保记录"""
        equipment = self.get_object()
        maintenance_records = EquipmentMaintenance.objects.filter(equipment=equipment)
        page = self.paginate_queryset(maintenance_records)
        if page is not None:
            serializer = EquipmentMaintenanceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EquipmentMaintenanceSerializer(maintenance_records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def applicable_spares(self, request, pk=None):
        """获取适用于该设备的备件列表"""
        equipment = self.get_object()
        spares = equipment.applicable_spares.all()
        page = self.paginate_queryset(spares)
        if page is not None:
            serializer = EquipmentSpareSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EquipmentSpareSerializer(spares, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def spare_usages(self, request, pk=None):
        """获取设备使用的备件记录"""
        equipment = self.get_object()
        spare_usages = EquipmentSpareInventory.objects.filter(related_equipment=equipment)
        page = self.paginate_queryset(spare_usages)
        if page is not None:
            serializer = EquipmentSpareInventorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EquipmentSpareInventorySerializer(spare_usages, many=True)
        return Response(serializer.data)


class EquipmentMaintenanceViewSet(viewsets.ModelViewSet):
    """设备维保记录视图集"""
    queryset = EquipmentMaintenance.objects.all()
    serializer_class = EquipmentMaintenanceSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['equipment__code', 'equipment__name', 'performed_by', 'description']
    filterset_fields = ['equipment', 'maintenance_type', 'maintenance_date']


class EquipmentSpareViewSet(viewsets.ModelViewSet):
    """设备备件视图集"""
    queryset = EquipmentSpare.objects.all()
    serializer_class = EquipmentSpareSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['code', 'name', 'model', 'manufacturer']
    
    @action(detail=True, methods=['get'])
    def inventory_records(self, request, pk=None):
        """获取备件的库存变动记录"""
        spare = self.get_object()
        inventory_records = EquipmentSpareInventory.objects.filter(spare=spare)
        page = self.paginate_queryset(inventory_records)
        if page is not None:
            serializer = EquipmentSpareInventorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EquipmentSpareInventorySerializer(inventory_records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inventory_status(self, request):
        """获取所有备件的库存状态，包括当前库存和最小库存信息"""
        queryset = self.get_queryset()
        
        # 获取每个备件的库存总和
        for spare in queryset:
            spare.current_inventory_value = spare.current_inventory
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_inventory(self, request):
        """获取库存不足的备件列表"""
        queryset = self.get_queryset()
        
        # 筛选库存低于最小库存的备件
        low_inventory_spares = []
        for spare in queryset:
            current = spare.current_inventory
            if current < spare.min_inventory:
                spare.current_inventory_value = current
                low_inventory_spares.append(spare)
                
        page = self.paginate_queryset(low_inventory_spares)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(low_inventory_spares, many=True)
        return Response(serializer.data)


class EquipmentSpareInventoryViewSet(viewsets.ModelViewSet):
    """备件库存记录视图集"""
    queryset = EquipmentSpareInventory.objects.all()
    serializer_class = EquipmentSpareInventorySerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['spare__code', 'spare__name', 'batch_no', 'remark']
    filterset_fields = ['spare', 'transaction_type', 'related_equipment', 'created_by'] 