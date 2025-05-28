import os
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import MaterialType,ProductCategory, CategoryParam, Product,ProductAttachment, ProductParamValue, Company, Process, ProcessCode, ProductProcessCode, ProcessDetail, BOM, BOMItem, Customer, Material, Unit, ProductCategoryProcessCode, CategoryMaterialRule, CategoryMaterialRuleParam
from utils.tools import convert_image_to_pdf

# Define Nested Serializers First
class CompanyNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'code']

class UnitNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'code']

class MaterialTypeNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialType
        fields = ['id', 'name', 'code']

class ProductParamValueSerializer(serializers.ModelSerializer):
    param_name = serializers.CharField(source='param.name', read_only=True)
    class Meta:
        model = ProductParamValue
        fields = ['id', 'product', 'param', 'param_name', 'value']

class MaterialSerializer(serializers.ModelSerializer):
    param_values = ProductParamValueSerializer(many=True, read_only=True)
    drawing_pdf_url = serializers.SerializerMethodField()
    drawing_pdf = serializers.FileField(allow_null=True, required=False)
    category_display_name = serializers.CharField(source='category.display_name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    material_type = MaterialTypeNestedSerializer(read_only=True)
    material_type_id = serializers.PrimaryKeyRelatedField(queryset=MaterialType.objects.all(), source='material_type', write_only=True, required=False, allow_null=True)

    def validate_code(self, value):
        qs = Product.objects.filter(code__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('物料代码已存在（不区分大小写）')
        return value

    def get_drawing_pdf_url(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        if obj.drawing_pdf and hasattr(obj.drawing_pdf, 'url') and obj.drawing_pdf.name:
            url = obj.drawing_pdf.url
            if request and not url.startswith('http'):
                return request.build_absolute_uri(url)
            return url
        return None

    def create(self, validated_data):
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
        model = Product
        fields = ['id', 'code', 'name', 'category', 'category_display_name', 'unit', 'unit_name', 'param_values', 'drawing_pdf', 'drawing_pdf_url', 'is_material', 'material_type', 'material_type_id']
        read_only_fields = ['is_material']

class ProductCategorySerializer(serializers.ModelSerializer):
    company = CompanyNestedSerializer(read_only=True)
    unit = UnitNestedSerializer(read_only=True)
    material_type = MaterialTypeNestedSerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), source='company', write_only=True)
    unit_id = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), source='unit', write_only=True, allow_null=True, required=False)
    material_type_id = serializers.PrimaryKeyRelatedField(queryset=MaterialType.objects.all(), source='material_type', write_only=True, allow_null=True, required=False)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

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
        if self.instance:
            company_id = self.instance.company_id
        else:
            company_id = self.initial_data.get('company_id')

        if company_id:
            qs = ProductCategory.objects.filter(code__iexact=value, company_id=company_id)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('同公司下产品类代码已存在（不区分大小写）')
        return value

    def validate_drawing_pdf(self, value):
        if value and hasattr(value, 'content_type'):
            if value.content_type.startswith('image/'):
                pdf_name = value.name.rsplit('.', 1)[0] + '.pdf'
                pdf_content, pdf_name = convert_image_to_pdf(value, pdf_name)
                if pdf_content:
                    pdf_content.name = pdf_name  # 确保ContentFile有name属性
                    print('[validate_drawing_pdf] 图片转PDF成功')
                    return pdf_content
                else:
                    print('[validate_drawing_pdf] 图片转PDF失败')
                    raise serializers.ValidationError('图片转PDF失败')
            if not (value.content_type == 'application/pdf' or value.content_type.startswith('image/')):
                raise serializers.ValidationError('仅支持PDF或图片文件')
            if value.size > 10 * 1024 * 1024:  # 10MB
                raise serializers.ValidationError('图纸文件不能超过10MB')
        return value

    def validate_process_pdf(self, value):
        if value and hasattr(value, 'content_type'):
            if value.content_type.startswith('image/'):
                pdf_name = value.name.rsplit('.', 1)[0] + '.pdf'
                pdf_content, pdf_name = convert_image_to_pdf(value, pdf_name)
                if pdf_content:
                    pdf_content.name = pdf_name  # 确保ContentFile有name属性
                    print('[validate_process_pdf] 图片转PDF成功')
                    return pdf_content
                else:
                    print('[validate_process_pdf] 图片转PDF失败')
                    raise serializers.ValidationError('图片转PDF失败')
            if not (value.content_type == 'application/pdf' or value.content_type.startswith('image/')):
                raise serializers.ValidationError('仅支持PDF或图片文件')
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
        if 'drawing_pdf' not in self.initial_data and not validated_data.get('drawing_pdf', None):
            validated_data.pop('drawing_pdf', None)

        if 'process_pdf' not in self.initial_data and not validated_data.get('process_pdf', None):
            validated_data.pop('process_pdf', None)

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
        fields = ['id', 'code', 'display_name', 'company', 'unit', 'material_type', 'company_id', 'unit_id', 'material_type_id', 'drawing_pdf', 'process_pdf', 'created_at']

class CategoryParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryParam
        fields = ['id', 'name', 'category', 'display_order']

    def validate(self, data):
        category = data.get('category', getattr(self.instance, 'category', None))
        name = data.get('name', getattr(self.instance, 'name', None))
        
        if not category:
            raise serializers.ValidationError({"category": "产品类不能为空。"})

        query = CategoryParam.objects.filter(category=category, name=name)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise serializers.ValidationError({
                "name": f"参数名称 '{name}' 已存在于选定的产品类中。"
            })
        return data

class MaterialTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialType
        fields = '__all__'

class ProductAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttachment
        fields = ['id', 'file', 'filename', 'uploaded_at']
        read_only_fields = ['filename', 'uploaded_at'] # filename和uploaded_at在上传时自动生成

    def create(self, validated_data):
        # 在这里处理文件上传时 filename 的设置
        file = validated_data.get('file')
        if file:
            validated_data['filename'] = file.name
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    param_values = ProductParamValueSerializer(many=True, read_only=True)
    drawing_pdf_url = serializers.SerializerMethodField()
    drawing_pdf = serializers.FileField(allow_null=True, required=False)
    category_display_name = serializers.CharField(source='category.display_name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    material_type = serializers.PrimaryKeyRelatedField(queryset=MaterialType.objects.all(), required=False, allow_null=True)
# 增加附件字段
    attachments = ProductAttachmentSerializer(many=True, read_only=True)
    def validate_code(self, value):
        qs = Product.objects.filter(code__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('产品代码已存在（不区分大小写）')
        return value

    def create(self, validated_data):
        if 'name' not in validated_data or not validated_data['name']:
            category = validated_data.get('category')
            if category:
                validated_data['name'] = category.display_name

        if 'is_material' not in validated_data:
            validated_data['is_material'] = False
        return super().create(validated_data)

    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'price', 'category', 'category_display_name', 'unit', 'unit_name', 'param_values', 'drawing_pdf', 'drawing_pdf_url', 'is_material', 'material_type','attachments']

    def get_drawing_pdf(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        if obj.drawing_pdf and hasattr(obj.drawing_pdf, 'url') and obj.drawing_pdf.name:
            file_path = os.path.join(settings.MEDIA_ROOT, obj.drawing_pdf.name)
            if os.path.exists(file_path):
                url = obj.drawing_pdf.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
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
    process_pdf = serializers.FileField(required=False, allow_null=True)
    product = serializers.SerializerMethodField()

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

    def validate(self, attrs):
        product = attrs.get('product') or (self.instance.product if self.instance else None)
        process_code = attrs.get('process_code') or (self.instance.process_code if self.instance else None)
        if product and process_code:
            qs = ProductProcessCode.objects.filter(product=product, process_code=process_code)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('该产品已关联此工艺流程代码')
        return attrs

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

    def to_representation(self, instance):
        """添加调试日志，查看序列化前后的数据"""
        print(f"--- ProductCategoryProcessCodeSerializer to_representation ---")
        print(f"Instance category_id: {instance.category_id}")
        data = super().to_representation(instance)
        print(f"Serialized data category: {data.get('category')}")
        return data

class ProcessDetailSerializer(serializers.ModelSerializer):
    process_code_display = serializers.CharField(source='process_code.code', read_only=True)
    process_code_version = serializers.CharField(source='process_code.version', read_only=True)
    step_name = serializers.CharField(source='step.name', read_only=True)
    step_code = serializers.CharField(source='step.code', read_only=True)
    program_file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProcessDetail
        fields = ['id', 'process_code', 'process_code_display', 'process_code_version', 'step_no', 'step', 'step_name', 'step_code', 'machine_time', 'labor_time', 'process_content', 'required_equipment', 'program_file', 'program_file_url']

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

class BOMItemSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    material_code = serializers.CharField(source='material.code', read_only=True)
    bom_name = serializers.CharField(source='bom.name', read_only=True)
    class Meta:
        model = BOMItem
        fields = ['id', 'bom', 'bom_name', 'material', 'material_name', 'material_code', 'quantity', 'remark']

class BOMSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    items = BOMItemSerializer(many=True, read_only=True)
    class Meta:
        model = BOM
        fields = ['id', 'product', 'product_name', 'name', 'version', 'description', 'created_at', 'updated_at', 'items']

class CategoryMaterialRuleParamSerializer(serializers.ModelSerializer):
    param_name = serializers.CharField(source='target_param.name', read_only=True)
    
    class Meta:
        model = CategoryMaterialRuleParam
        fields = ['id', 'rule', 'target_param', 'param_name', 'expression']

class CategoryMaterialRuleSerializer(serializers.ModelSerializer):
    source_category_name = serializers.CharField(source='source_category.display_name', read_only=True)
    source_category_code = serializers.CharField(source='source_category.code', read_only=True)
    target_category_name = serializers.CharField(source='target_category.display_name', read_only=True)
    target_category_code = serializers.CharField(source='target_category.code', read_only=True)
    param_expressions = CategoryMaterialRuleParamSerializer(many=True, read_only=True)
    
    class Meta:
        model = CategoryMaterialRule
        fields = ['id', 'source_category', 'source_category_name', 'source_category_code', 
                 'target_category', 'target_category_name', 'target_category_code',
                 'created_at', 'updated_at', 'param_expressions']

