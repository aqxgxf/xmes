from django.contrib import admin
from .models import Equipment, EquipmentMaintenance, EquipmentSpare, EquipmentSpareInventory

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'model', 'status', 'location', 'responsible_person', 'next_maintenance_date')
    list_filter = ('status', 'location')
    search_fields = ('code', 'name', 'model', 'manufacturer')
    date_hierarchy = 'created_at'

@admin.register(EquipmentMaintenance)
class EquipmentMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'maintenance_date', 'maintenance_type', 'performed_by', 'next_maintenance_date')
    list_filter = ('maintenance_type', 'maintenance_date')
    search_fields = ('equipment__code', 'equipment__name', 'performed_by', 'description')
    date_hierarchy = 'maintenance_date'

@admin.register(EquipmentSpare)
class EquipmentSpareAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'model', 'unit', 'price', 'min_inventory')
    list_filter = ('manufacturer',)
    search_fields = ('code', 'name', 'model', 'manufacturer')
    filter_horizontal = ('applicable_equipment',)

@admin.register(EquipmentSpareInventory)
class EquipmentSpareInventoryAdmin(admin.ModelAdmin):
    list_display = ('spare', 'transaction_type', 'quantity', 'transaction_date', 'related_equipment', 'created_by')
    list_filter = ('transaction_type', 'transaction_date')
    search_fields = ('spare__code', 'spare__name', 'batch_no', 'remark')
    date_hierarchy = 'transaction_date' 