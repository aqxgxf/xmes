import json
from rest_framework import viewsets, status, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
import pandas as pd
from django.db import transaction
from rest_framework.response import Response
from rest_framework import filters
from .models import ProductCategory, CategoryParam, Product, ProductParamValue, Company, Process, ProcessCode, ProductProcessCode, ProcessDetail, BOM, BOMItem, Customer, Material
from .serializers import ProductCategorySerializer, CategoryParamSerializer, ProductSerializer, ProductParamValueSerializer, CompanySerializer, ProcessSerializer, ProcessCodeSerializer, ProductProcessCodeSerializer, ProcessDetailSerializer, BOMSerializer, BOMItemSerializer, CustomerSerializer, MaterialSerializer
from rest_framework import viewsets

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
    queryset = Product.objects.filter(is_material=False)
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

    def create(self, request, *args, **kwargs):
        # print('class ProduceViewSet\def create\FILES值为:', request.FILES)
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
        # print("class ProduceViewSet\def create\drawing_pdf值为", drawing_pdf)
        # print("class ProduceViewSet\def create\serializer值为", serializer)
        product = serializer.save()
        for pv in param_values:
            if isinstance(pv, dict):
                ProductParamValue.objects.create(product=product, param_id=pv.get('param'), value=pv.get('value'))
        # print("class ProduceViewSet\def create\product.drawing_pdf值为", product.drawing_pdf)
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
        # print('param_values for update:', param_values)
        for pv in param_values:
            if isinstance(pv, dict):
                print('Creating ProductParamValue:', pv)
                ProductParamValue.objects.create(product=product, param_id=pv.get('param'), value=pv.get('value'))
        return Response(self.get_serializer(product).data)

    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser])
    def import_products(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'msg': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return Response({'msg': f'文件解析失败: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        required_cols = ['code', 'name', 'price', 'category']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)
        from .models import Product, ProductCategory
        success, fail = 0, 0
        fail_msgs = []
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    category_obj = ProductCategory.objects.filter(name=row['category']).first()
                    if not category_obj:
                        fail += 1
                        fail_msgs.append(f"第{idx+2}行: 产品类不存在")
                        continue
                    Product.objects.update_or_create(
                        code=row['code'],
                        defaults={
                            'name': row['name'],
                            'price': row['price'],
                            'category': category_obj,
                            'is_material': False
                        }
                    )
                    success += 1
                except Exception as e:
                    fail += 1
                    fail_msgs.append(f"第{idx+2}行: {e}")
        msg = f"导入完成，成功{success}条，失败{fail}条。"
        if fail:
            msg += ' 错误: ' + '; '.join(fail_msgs[:5])
        return Response({'msg': msg})

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

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    pagination_class = StandardResultsSetPagination

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']
    
    def get_queryset(self):
        # 直接使用Product模型过滤，确保只返回物料
        return Product.objects.filter(is_material=True)
        
    def create(self, request, *args, **kwargs):
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
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        drawing_pdf = request.FILES.get('drawing_pdf', None)
        if not drawing_pdf or (hasattr(drawing_pdf, 'name') and not drawing_pdf.name) or (hasattr(drawing_pdf, 'size') and drawing_pdf.size == 0):
            serializer.validated_data['drawing_pdf'] = None
        
        # 保存物料
        material = serializer.save()
        
        # 创建参数值
        for pv in param_values:
            if isinstance(pv, dict):
                ProductParamValue.objects.create(product=material, param_id=pv.get('param'), value=pv.get('value'))
        
        return Response(self.get_serializer(material).data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        
        # 处理参数值
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
        
        # 处理图纸
        drawing_pdf = request.FILES.get('drawing_pdf', None)
        if not drawing_pdf or (hasattr(drawing_pdf, 'name') and not drawing_pdf.name) or (hasattr(drawing_pdf, 'size') and drawing_pdf.size == 0):
            serializer.validated_data['drawing_pdf'] = None
        
        # 保存物料
        material = serializer.save()
        
        # 更新参数值
        ProductParamValue.objects.filter(product=material).delete()
        for pv in param_values:
            if isinstance(pv, dict):
                ProductParamValue.objects.create(product=material, param_id=pv.get('param'), value=pv.get('value'))
        
        return Response(self.get_serializer(material).data)
        
    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser])
    def import_materials(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'msg': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return Response({'msg': f'文件解析失败: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        required_cols = ['code', 'name', 'price', 'category']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)
        success, fail = 0, 0
        fail_msgs = []
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    category_obj = ProductCategory.objects.filter(name=row['category']).first()
                    if not category_obj:
                        fail += 1
                        fail_msgs.append(f"第{idx+2}行: 物料类不存在")
                        continue
                    Product.objects.update_or_create(
                        code=row['code'],
                        defaults={
                            'name': row['name'],
                            'price': row['price'],
                            'category': category_obj,
                            'is_material': True
                        }
                    )
                    success += 1
                except Exception as e:
                    fail += 1
                    fail_msgs.append(f"第{idx+2}行: {e}")
        msg = f"导入完成，成功{success}条，失败{fail}条。"
        if fail:
            msg += ' 错误: ' + '; '.join(fail_msgs[:5])
        return Response({'msg': msg})

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
    
    def get_queryset(self):
        queryset = ProductProcessCode.objects.all().order_by('id')
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

class ProcessDetailViewSet(viewsets.ModelViewSet):
    queryset = ProcessDetail.objects.all().order_by('process_code', 'step_no')
    serializer_class = ProcessDetailSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['process_code__code', 'step__name', 'step_no']

    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser])
    def import_process_details(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'msg': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return Response({'msg': f'文件解析失败: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        required_cols = ['process_code', 'step_no', 'step', 'machine_time', 'labor_time']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)
        success, fail = 0, 0
        fail_msgs = []
        from .models import ProcessCode, Process, ProcessDetail
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    process_code_obj = ProcessCode.objects.filter(code=row['process_code']).first()
                    step_obj = Process.objects.filter(name=row['step']).first()
                    if not process_code_obj or not step_obj:
                        fail += 1
                        fail_msgs.append(f"第{idx+2}行: 工艺流程代码或工序不存在")
                        continue
                    ProcessDetail.objects.update_or_create(
                        process_code=process_code_obj,
                        step_no=row['step_no'],
                        defaults={
                            'step': step_obj,
                            'machine_time': row['machine_time'],
                            'labor_time': row['labor_time']
                        }
                    )
                    success += 1
                except Exception as e:
                    fail += 1
                    fail_msgs.append(f"第{idx+2}行: {e}")
        msg = f"导入完成，成功{success}条，失败{fail}条。"
        if fail:
            msg += ' 错误: ' + '; '.join(fail_msgs[:5])
        return Response({'msg': msg})

class BOMViewSet(viewsets.ModelViewSet):
    queryset = BOM.objects.all().order_by('-created_at')
    serializer_class = BOMSerializer

class BOMItemViewSet(viewsets.ModelViewSet):
    queryset = BOMItem.objects.all()
    serializer_class = BOMItemSerializer
