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
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

    def create(self, request, *args, **kwargs):
        print('class ProduceViewSet\def create\FILES值为:', request.FILES)
        data = request.data.copy()
        param_values = data.pop('param_values', [])
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
        if param_values and isinstance(param_values, list) and isinstance(param_values[0], list):
            param_values = [item for sublist in param_values for item in sublist]
        # 只用data=data，DRF自动处理文件
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        drawing_pdf = request.FILES.get('drawing_pdf', None)
        if not drawing_pdf or (hasattr(drawing_pdf, 'name') and not drawing_pdf.name) or (hasattr(drawing_pdf, 'size') and drawing_pdf.size == 0):
            serializer.validated_data['drawing_pdf'] = None
        print("class ProduceViewSet\def create\drawing_pdf值为", drawing_pdf)
        print("class ProduceViewSet\def create\serializer值为", serializer)
        product = serializer.save()
        for pv in param_values:
            if isinstance(pv, dict):
                ProductParamValue.objects.create(product=product, param_id=pv.get('param'), value=pv.get('value'))
        print("class ProduceViewSet\def create\product.drawing_pdf值为", product.drawing_pdf)
        return Response(self.get_serializer(product).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        param_values = data.pop('param_values', [])
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
        if param_values and isinstance(param_values, list) and isinstance(param_values[0], list):
            param_values = [item for sublist in param_values for item in sublist]
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        drawing_pdf = request.FILES.get('drawing_pdf', None)
        if not drawing_pdf or (hasattr(drawing_pdf, 'name') and not drawing_pdf.name) or (hasattr(drawing_pdf, 'size') and drawing_pdf.size == 0):
            serializer.validated_data['drawing_pdf'] = None
        product = serializer.save()
        ProductParamValue.objects.filter(product=product).delete()
        print('param_values for update:', param_values)
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
