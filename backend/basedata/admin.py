from django.contrib import admin
from .models import ProductCategory, CategoryParam, Product, Company, Process, ProcessCode, ProductProcessCode, ProcessDetail, BOM, BOMItem, Unit

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'display_name', 'company')
    search_fields = ('code', 'display_name')
    list_filter = ('company',)

@admin.register(CategoryParam)
class CategoryParamAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'price', 'category', 'unit', 'is_material')
    search_fields = ('code', 'name')
    list_filter = ('category', 'is_material', 'unit')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'contact', 'phone')
    search_fields = ('name', 'code', 'contact')

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name', 'description')

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')

@admin.register(ProcessCode)
class ProcessCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'version', 'description')
    search_fields = ('code', 'version')

@admin.register(ProductProcessCode)
class ProductProcessCodeAdmin(admin.ModelAdmin):
    list_display = ('product', 'process_code', 'is_default')
    list_filter = ('is_default',)

@admin.register(ProcessDetail)
class ProcessDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'process_code', 'step', 'step_no', 'machine_time', 'labor_time')
    list_filter = ('process_code',)
    search_fields = ('step__name',)

@admin.register(BOM)
class BOMAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'version', 'created_at', 'updated_at')
    search_fields = ('product__name', 'name', 'version')
    list_filter = ('product',)

@admin.register(BOMItem)
class BOMItemAdmin(admin.ModelAdmin):
    list_display = ('bom', 'material', 'quantity')
    search_fields = ('bom__name', 'material__name')
    list_filter = ('bom',)
