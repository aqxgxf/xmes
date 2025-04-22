import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from rest_framework import filters
from .models import ProductCategory, CategoryParam, Product, ProductParamValue, Company, Process, ProcessCode, ProductProcessCode, ProcessDetail
from .serializers import ProductCategorySerializer, CategoryParamSerializer, ProductSerializer, ProductParamValueSerializer, CompanySerializer, ProcessSerializer, ProcessCodeSerializer, ProductProcessCodeSerializer, ProcessDetailSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all().order_by('id')
    serializer_class = ProductCategorySerializer
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=['get'])
    def params(self, request, pk=None):
        params = CategoryParam.objects.filter(category_id=pk)
        page = self.paginate_queryset(params)
        if page is not None:
            serializer = CategoryParamSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CategoryParamSerializer(params, many=True)
        return Response(serializer.data)

class CategoryParamViewSet(viewsets.ModelViewSet):
    queryset = CategoryParam.objects.all()
    serializer_class = CategoryParamSerializer
    pagination_class = StandardResultsSetPagination

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

    def create(self, request, *args, **kwargs):
        # 创建产品及参数值
        data = request.data.copy()
        param_values = data.pop('param_values', [])
        # 只在字符串时反序列化一次，其他情况直接用
        if isinstance(param_values, str):
            try:
                param_values = json.loads(param_values)
            except Exception:
                param_values = []
        # 兼容字符串列表（如 ['{"param":1,"value":"xxx"}', ...]）
        if isinstance(param_values, list) and param_values and isinstance(param_values[0], str):
            try:
                param_values = [json.loads(x) for x in param_values]
            except Exception:
                param_values = []
        # 拍平 param_values 如果是列表的列表
        if param_values and isinstance(param_values, list) and isinstance(param_values[0], list):
            param_values = [item for sublist in param_values for item in sublist]
        # param_values 应该是 list of dict
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        # 调试输出
        print('param_values for create:', param_values)
        for pv in param_values:
            if isinstance(pv, dict):
                print('Creating ProductParamValue:', pv)
                ProductParamValue.objects.create(product=product, param_id=pv.get('param'), value=pv.get('value'))
        # 自动修复：如果产品的drawing_pdf为空，补充所属产品类的drawing_pdf
        if not product.drawing_pdf and product.category and hasattr(product.category, 'drawing_pdf') and product.category.drawing_pdf:
            product.drawing_pdf = product.category.drawing_pdf
            product.save(update_fields=['drawing_pdf'])
        return Response(self.get_serializer(product).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # 更新产品及参数值
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()  # 修复：copy一份可变的QueryDict
        param_values = data.pop('param_values', [])
        # 只在字符串时反序列化一次，其他情况直接用
        if isinstance(param_values, str):
            try:
                param_values = json.loads(param_values)
            except Exception:
                param_values = []
        if isinstance(param_values, list) and param_values and isinstance(param_values[0], str):
            try:
                param_values = [json.loads(x) for x in param_values]
            except Exception:
                param_values = []
        # 拍平 param_values 如果是列表的列表
        if param_values and isinstance(param_values, list) and isinstance(param_values[0], list):
            param_values = [item for sublist in param_values for item in sublist]
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        # 先删除原有参数项
        ProductParamValue.objects.filter(product=product).delete()
        # 调试输出
        print('param_values for update:', param_values)
        # 再写入新参数项
        for pv in param_values:
            if isinstance(pv, dict):
                print('Creating ProductParamValue:', pv)
                ProductParamValue.objects.create(product=product, param_id=pv.get('param'), value=pv.get('value'))
        return Response(self.get_serializer(product).data)

class ProductParamValueViewSet(viewsets.ModelViewSet):
    queryset = ProductParamValue.objects.all()
    serializer_class = ProductParamValueSerializer

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'code', 'address', 'contact', 'phone']

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all().order_by('id')
    serializer_class = ProcessSerializer
    pagination_class = StandardResultsSetPagination

class ProcessCodeViewSet(viewsets.ModelViewSet):
    queryset = ProcessCode.objects.all().order_by('id')
    serializer_class = ProcessCodeSerializer
    pagination_class = StandardResultsSetPagination

class ProductProcessCodeViewSet(viewsets.ModelViewSet):
    queryset = ProductProcessCode.objects.all().order_by('id')
    serializer_class = ProductProcessCodeSerializer
    pagination_class = StandardResultsSetPagination

class ProcessDetailViewSet(viewsets.ModelViewSet):
    queryset = ProcessDetail.objects.all().order_by('process_code', 'step_no')
    serializer_class = ProcessDetailSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['process_code__code', 'step__name', 'step_no']
