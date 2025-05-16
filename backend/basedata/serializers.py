import os
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import ProductCategory, CategoryParam, Product, ProductParamValue, Company, Process, ProcessCode, ProductProcessCode, ProcessDetail, BOM, BOMItem, Customer, Material, Unit, ProductCategoryProcessCode

class ProductCategorySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
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

    def validate_code(self, value):
        company = self.initial_data.get('company') or getattr(self.instance, 'company_id', None)
        qs = ProductCategory.objects.filter(code__iexact=value, company_id=company)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('同公司下产品类代码已存在（不区分大小写）')
        return value

    def validate_drawing_pdf(self, value):
        if value and hasattr(value, 'content_type'):
            if not (value.content_type == 'application/pdf' or value.content_type.startswith('image/')):
                raise serializers.ValidationError('图纸文件必须是PDF或图片格式')

            # 检查文件大小
            if value.size > 10 * 1024 * 1024:  # 10MB
                raise serializers.ValidationError('图纸文件不能超过10MB')
        return value

    def validate_process_pdf(self, value):
        if value and hasattr(value, 'content_type'):
            if not (value.content_type == 'application/pdf' or value.content_type.startswith('image/')):
                raise serializers.ValidationError('工艺文件必须是PDF或图片格式')

            # 检查文件大小
            if value.size > 10 * 1024 * 1024:  # 10MB
                raise serializers.ValidationError('工艺文件不能超过10MB')
        return value

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ValueError as e:
            error_msg = str(e)
            if "上传的图纸文件不是有效的PDF格式" in error_msg:
                raise serializers.ValidationError({"drawing_pdf": "上传的图纸文件不是有效的PDF格式"})
            elif "图纸文件格式无效" in error_msg:
                raise serializers.ValidationError({"drawing_pdf": "图纸文件格式无效，仅支持PDF或可转换为PDF的图片格式"})
            elif "上传的工艺文件不是有效的PDF格式" in error_msg:
                raise serializers.ValidationError({"process_pdf": "上传的工艺文件不是有效的PDF格式"})
            elif "工艺文件格式无效" in error_msg:
                raise serializers.ValidationError({"process_pdf": "工艺文件格式无效，仅支持PDF或可转换为PDF的图片格式"})
            raise

    def update(self, instance, validated_data):
        # 如果没有新上传的文件，保持原有文件
        if 'drawing_pdf' not in self.initial_data and not validated_data.get('drawing_pdf', None):
            validated_data.pop('drawing_pdf', None)  # 移除空值但不覆盖现有值

        if 'process_pdf' not in self.initial_data and not validated_data.get('process_pdf', None):
            validated_data.pop('process_pdf', None)  # 移除空值但不覆盖现有值

        try:
            return super().update(instance, validated_data)
        except ValueError as e:
            error_msg = str(e)
            if "上传的图纸文件不是有效的PDF格式" in error_msg:
                raise serializers.ValidationError({"drawing_pdf": "上传的图纸文件不是有效的PDF格式"})
            elif "图纸文件格式无效" in error_msg:
                raise serializers.ValidationError({"drawing_pdf": "图纸文件格式无效，仅支持PDF或可转换为PDF的图片格式"})
            elif "上传的工艺文件不是有效的PDF格式" in error_msg:
                raise serializers.ValidationError({"process_pdf": "上传的工艺文件不是有效的PDF格式"})
            elif "工艺文件格式无效" in error_msg:
                raise serializers.ValidationError({"process_pdf": "工艺文件格式无效，仅支持PDF或可转换为PDF的图片格式"})
            raise

    class Meta:
        model = ProductCategory
        fields = ['id', 'code', 'display_name', 'company', 'company_name', 'unit', 'unit_name', 'drawing_pdf', 'process_pdf']

class CategoryParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryParam
        fields = '__all__'

class ProductParamValueSerializer(serializers.ModelSerializer):
    param_name = serializers.CharField(source='param.name', read_only=True)
    class Meta:
        model = ProductParamValue
        fields = ['id', 'product', 'param', 'param_name', 'value']

class ProductSerializer(serializers.ModelSerializer):
    param_values = ProductParamValueSerializer(many=True, read_only=True)
    drawing_pdf_url = serializers.SerializerMethodField()
    drawing_pdf = serializers.FileField(allow_null=True, required=False)  # 修改为FileField
    category_display_name = serializers.CharField(source='category.display_name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)

    def validate_code(self, value):
        qs = Product.objects.filter(code__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('产品代码已存在（不区分大小写）')
        return value

    def create(self, validated_data):
        # 如果没有提供名称，使用category的display_name
        if 'name' not in validated_data or not validated_data['name']:
            category = validated_data.get('category')
            if category:
                validated_data['name'] = category.display_name

        # 确保产品默认非物料
        if 'is_material' not in validated_data:
            validated_data['is_material'] = False
        return super().create(validated_data)

    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'price', 'category', 'category_display_name', 'unit', 'unit_name', 'param_values', 'drawing_pdf', 'drawing_pdf_url', 'is_material']

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
    product_code = serializers.CharField(source='product.code', read_only=True)
    process_code_text = serializers.CharField(source='process_code.code', read_only=True)
    process_code_version = serializers.CharField(source='process_code.version', read_only=True)

    class Meta:
        model = ProductProcessCode
        fields = '__all__'

class ProductCategoryProcessCodeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)
    process_code_text = serializers.CharField(source='process_code.code', read_only=True)
    process_code_version = serializers.CharField(source='process_code.version', read_only=True)

    class Meta:
        model = ProductCategoryProcessCode
        fields = '__all__'

class ProcessDetailSerializer(serializers.ModelSerializer):
    process_code_display = serializers.CharField(source='process_code.code', read_only=True)
    process_code_version = serializers.CharField(source='process_code.version', read_only=True)
    step_name = serializers.CharField(source='step.name', read_only=True)
    step_code = serializers.CharField(source='step.code', read_only=True)
    program_file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProcessDetail
        fields = ['id', 'process_code', 'process_code_display', 'process_code_version', 'step_no', 'step', 'step_name', 'step_code', 'machine_time', 'labor_time', 'process_content', 'program_file', 'program_file_url']

    def get_program_file_url(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        url = obj.program_file.url if obj.program_file else None
        if url and request and not url.startswith('http'):
            return request.build_absolute_uri(url)
        return url

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'code', 'name', 'description']

class MaterialSerializer(serializers.ModelSerializer):
    param_values = ProductParamValueSerializer(many=True, read_only=True)
    drawing_pdf_url = serializers.SerializerMethodField()
    drawing_pdf = serializers.FileField(allow_null=True, required=False)
    category_display_name = serializers.CharField(source='category.display_name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)

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
        # 如果没有提供名称，使用category的display_name
        if 'name' not in validated_data or not validated_data['name']:
            category = validated_data.get('category')
            if category:
                validated_data['name'] = category.display_name

        validated_data['is_material'] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['is_material'] = True
        return super().update(instance, validated_data)

    class Meta:
        model = Material
        fields = ['id', 'code', 'name', 'price', 'category', 'category_display_name', 'unit', 'unit_name', 'param_values', 'drawing_pdf', 'drawing_pdf_url', 'is_material']
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

