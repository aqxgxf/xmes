import os
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import ProductCategory, CategoryParam, Product, ProductParamValue, Company, Process, ProcessCode, ProductProcessCode, ProcessDetail, BOM, BOMItem, Customer, Material

class ProductCategorySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    # 保持和图纸pdf一致，直接返回process_pdf的url
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request') if hasattr(self, 'context') else None
        # 图纸pdf
        if instance.drawing_pdf and hasattr(instance.drawing_pdf, 'url') and instance.drawing_pdf.name:
            url = instance.drawing_pdf.url
            if request and not url.startswith('http'):
                url = request.build_absolute_uri(url)
            data['drawing_pdf'] = url
        else:
            data['drawing_pdf'] = None
        # 工艺pdf
        if instance.process_pdf and hasattr(instance.process_pdf, 'url') and instance.process_pdf.name:
            url = instance.process_pdf.url
            if request and not url.startswith('http'):
                url = request.build_absolute_uri(url)
            data['process_pdf'] = url
        else:
            data['process_pdf'] = None
        return data

    def validate_name(self, value):
        company = self.initial_data.get('company') or getattr(self.instance, 'company_id', None)
        qs = ProductCategory.objects.filter(name__iexact=value, company_id=company)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('同公司下产品类名称已存在（不区分大小写）')
        return value
    def update(self, instance, validated_data):
        # 如果没有新上传的文件，保持原有文件
        if 'drawing_pdf' not in self.initial_data and not validated_data.get('drawing_pdf', None):
            validated_data['drawing_pdf'] = instance.drawing_pdf
        if 'process_pdf' not in self.initial_data and not validated_data.get('process_pdf', None):
            validated_data['process_pdf'] = instance.process_pdf
        return super().update(instance, validated_data)
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
    drawing_pdf = serializers.FileField(allow_null=True, required=False)  # 修改为FileField
    def validate_code(self, value):
        qs = Product.objects.filter(code__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('产品代码已存在（不区分大小写）')
        return value
        
    def create(self, validated_data):
        # 确保产品默认非物料
        if 'is_material' not in validated_data:
            validated_data['is_material'] = False
        return super().create(validated_data)
        
    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'price', 'category', 'param_values', 'drawing_pdf', 'drawing_pdf_url', 'is_material']

    def get_drawing_pdf(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        # 优先返回产品自身的图纸PDF
        if obj.drawing_pdf and hasattr(obj.drawing_pdf, 'url') and obj.drawing_pdf.name:
            file_path = os.path.join(settings.MEDIA_ROOT, obj.drawing_pdf.name)
            if os.path.exists(file_path):
                url = obj.drawing_pdf.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
        # 如果产品没有，返回所属产品类的图纸PDF
        if obj.category and obj.category.drawing_pdf and hasattr(obj.category.drawing_pdf, 'url') and obj.category.drawing_pdf.name:
            file_path = os.path.join(settings.MEDIA_ROOT, obj.category.drawing_pdf.name)
            if os.path.exists(file_path):
                url = obj.category.drawing_pdf.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
        return None

    def get_drawing_pdf_url(self, obj):
        return self.get_drawing_pdf(obj)

    def update(self, instance, validated_data):
        # 不主动pop drawing_pdf，交给DRF处理
        return super().update(instance, validated_data)

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'code', 'address', 'contact', 'phone']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'code', 'address', 'contact', 'phone']

class ProcessSerializer(serializers.ModelSerializer):
    def validate_code(self, value):
        qs = Process.objects.filter(code__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('工序代码已存在（不区分大小写）')
        return value
    def validate_name(self, value):
        qs = Process.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('工序名称已存在（不区分大小写）')
        return value
    class Meta:
        model = Process
        fields = ['id', 'name', 'code', 'description', 'created_at', 'updated_at']

class ProcessCodeSerializer(serializers.ModelSerializer):
    process_pdf = serializers.FileField(required=False, allow_null=True)  # 新增
    product = serializers.SerializerMethodField()  # 新增

    def get_product(self, obj):
        rel = ProductProcessCode.objects.filter(process_code=obj, is_default=True).first()
        print(f'ProcessCode id={obj.id}, get_product called, rel={rel}')
        return rel.product.id if rel else None
    def validate(self, attrs):
        code = attrs.get('code', getattr(self.instance, 'code', None))
        version = attrs.get('version', getattr(self.instance, 'version', None))
        qs = ProcessCode.objects.filter(code__iexact=code, version=version)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({'code': '同版本下工艺流程代码已存在（不区分大小写）'})
        return attrs

    class Meta:
        model = ProcessCode
        fields = '__all__'

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

class MaterialSerializer(serializers.ModelSerializer):
    param_values = ProductParamValueSerializer(many=True, read_only=True)
    drawing_pdf_url = serializers.SerializerMethodField()
    drawing_pdf = serializers.FileField(allow_null=True, required=False)
    
    def validate_code(self, value):
        qs = Product.objects.filter(code__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('物料代码已存在（不区分大小写）')
        return value
        
    def get_drawing_pdf_url(self, obj):
        # 与ProductSerializer保持一致，提供图纸URL
        request = self.context.get('request') if hasattr(self, 'context') else None
        if obj.drawing_pdf and hasattr(obj.drawing_pdf, 'url') and obj.drawing_pdf.name:
            url = obj.drawing_pdf.url
            if request and not url.startswith('http'):
                return request.build_absolute_uri(url)
            return url
        return None
        
    def create(self, validated_data):
        validated_data['is_material'] = True
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        validated_data['is_material'] = True
        return super().update(instance, validated_data)
        
    class Meta:
        model = Material
        fields = ['id', 'code', 'name', 'price', 'category', 'param_values', 'drawing_pdf', 'drawing_pdf_url', 'is_material']
        read_only_fields = ['is_material']

class BOMItemSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    bom_name = serializers.CharField(source='bom.name', read_only=True)
    class Meta:
        model = BOMItem
        fields = ['id', 'bom', 'bom_name', 'material', 'material_name', 'quantity', 'remark']

class BOMSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    items = BOMItemSerializer(many=True, read_only=True)
    class Meta:
        model = BOM
        fields = ['id', 'product', 'product_name', 'name', 'version', 'description', 'created_at', 'updated_at', 'items']

