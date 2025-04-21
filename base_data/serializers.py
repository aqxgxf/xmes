from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import ProductCategory, CategoryParam, Product, ProductParamValue, Company

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

