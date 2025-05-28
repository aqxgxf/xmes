from django.contrib import admin
from .models import MaterialType,ProductCategory, CategoryParam, Product, ProductParamValue, Process, ProcessCode, ProductProcessCode, ProcessDetail, BOM, BOMItem, Company, Material, Unit, CategoryMaterialRule, CategoryMaterialRuleParam, ProductCategoryProcessCode

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'company')
    search_fields = ('display_name', 'code')
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

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
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
    list_filter = ('is_default', 'product', 'process_code')
    search_fields = ('product__name', 'product__code', 'process_code__code')

@admin.register(ProductCategoryProcessCode)
class ProductCategoryProcessCodeAdmin(admin.ModelAdmin):
    list_display = ('category', 'process_code', 'is_default')
    list_filter = ('is_default', 'category', 'process_code')
    search_fields = ('category__display_name', 'category__code', 'process_code__code')

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

@admin.register(CategoryMaterialRule)
class CategoryMaterialRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_category', 'target_category', 'created_at', 'updated_at')
    list_filter = ('source_category', 'target_category')
    search_fields = ('source_category__code', 'source_category__display_name', 
                     'target_category__code', 'target_category__display_name')

@admin.register(CategoryMaterialRuleParam)
class CategoryMaterialRuleParamAdmin(admin.ModelAdmin):
    list_display = ('id', 'rule', 'target_param', 'expression')
    list_filter = ('rule',)
    search_fields = ('target_param__name', 'expression')

@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "description")
    search_fields = ("name", "code")
