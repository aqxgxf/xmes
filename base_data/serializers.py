from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import ProductCategory, CategoryParam, Product, ProductParamValue, Company, Process, ProcessCode, ProductProcessCode, ProcessDetail

class ProductCategorySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    class Meta:
        model = ProductCategory
        fields = '__all__'
        extra_fields = ['company_name']

class CategoryParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryParam
        fields = '__all__'

class ProductParamValueSerializer(serializers.ModelSerializer):
    param_name = serializers.CharField(source='param.name', read_only=True)
    class Meta:
        model = ProductParamValue
        fields = ['id', 'param', 'param_name', 'value']

class ProductSerializer(serializers.ModelSerializer):
    param_values = ProductParamValueSerializer(many=True, read_only=True)
    drawing_pdf_url = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'price', 'category', 'param_values', 'drawing_pdf', 'drawing_pdf_url']
    def get_drawing_pdf_url(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        url = obj.get_drawing_pdf()
        if url and request and not url.startswith('http'):
            # 保证返回绝对路径，防止前端拼接出错
            return request.build_absolute_uri(url)
        return url

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'code', 'address', 'contact', 'phone']

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['id', 'name', 'code', 'description', 'created_at', 'updated_at']

class ProcessCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessCode
        fields = ['id', 'code', 'description', 'version', 'created_at', 'updated_at']

class ProductProcessCodeSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    process_code_detail = ProcessCodeSerializer(source='process_code', read_only=True)
    class Meta:
        model = ProductProcessCode
        fields = ['id', 'product', 'product_name', 'process_code', 'process_code_detail', 'is_default']

class ProcessDetailSerializer(serializers.ModelSerializer):
    process_code_display = serializers.CharField(source='process_code.code', read_only=True)
    process_code_version = serializers.CharField(source='process_code.version', read_only=True)
    step_name = serializers.CharField(source='step.name', read_only=True)
    step_code = serializers.CharField(source='step.code', read_only=True)
    program_file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProcessDetail
        fields = ['id', 'process_code', 'process_code_display', 'process_code_version', 'step_no', 'step', 'step_name', 'step_code', 'machine_time', 'labor_time', 'program_file', 'program_file_url']

    def get_program_file_url(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        url = obj.program_file.url if obj.program_file else None
        if url and request and not url.startswith('http'):
            return request.build_absolute_uri(url)
        return url

