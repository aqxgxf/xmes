import json
from rest_framework import viewsets, status, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
import pandas as pd
from django.db import transaction
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductCategory, CategoryParam, Product, ProductParamValue, Company, Process, ProcessCode, ProductProcessCode, ProcessDetail, BOM, BOMItem, Customer, Material, Unit, ProductCategoryProcessCode, CategoryMaterialRule, CategoryMaterialRuleParam
from .serializers import ProductCategorySerializer, CategoryParamSerializer, ProductSerializer, ProductParamValueSerializer, CompanySerializer, ProcessSerializer, ProcessCodeSerializer, ProductProcessCodeSerializer, ProcessDetailSerializer, BOMSerializer, BOMItemSerializer, CustomerSerializer, MaterialSerializer, UnitSerializer, ProductCategoryProcessCodeSerializer, CategoryMaterialRuleSerializer, CategoryMaterialRuleParamSerializer
from rest_framework import viewsets
from django.core.files.storage import default_storage
import os
import re
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from openpyxl import Workbook
import io
import logging

class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all().order_by('code')
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'code']
    search_fields = ['code', 'display_name']
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['code', 'display_name', 'company__name']
    ordering = ['code']

    @action(detail=True, methods=['get'])
    def params(self, request, pk=None):
        params = CategoryParam.objects.filter(category_id=pk)
        page = self.paginate_queryset(params)
        if page is not None:
            serializer = CategoryParamSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CategoryParamSerializer(params, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='export-params')
    def export_params(self, request):
        """导出产品类和对应的参数项到Excel"""
        # 创建工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = "产品类参数"

        # 设置表头
        ws.append(["产品类", "参数项"])

        # 获取所有产品类
        categories = ProductCategory.objects.all().order_by('code')

        # 对每个产品类，获取其所有参数项并用逗号拼接
        for category in categories:
            params = CategoryParam.objects.filter(category=category).order_by('name')
            param_names = ', '.join([param.name for param in params])
            category_name = f"{category.code} - {category.display_name}"
            ws.append([category_name, param_names])

        # 设置列宽
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 80

        # 保存到内存缓冲区
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        # 创建HTTP响应
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=产品类参数列表.xlsx'

        return response

    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser])
    def import_categories(self, request):
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

        required_cols = ['code', 'display_name', 'company']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)

        from .models import Company

        success_count = 0
        fail_count = 0
        fail_msgs = []

        for index, row in df.iterrows():
            try:
                # Get company by name
                company = Company.objects.filter(name=row['company']).first()
                if not company:
                    fail_msgs.append(f'第{index+1}行: 找不到公司: {row["company"]}')
                    fail_count += 1
                    continue

                # Create or update category
                category, created = ProductCategory.objects.update_or_create(
                    code=row['code'],
                    company=company,
                    defaults={
                        'display_name': row['display_name']
                    }
                )

                success_count += 1
            except Exception as e:
                fail_count += 1
                fail_msgs.append(f'第{index+1}行: {str(e)}')

        return Response({
            'msg': '产品类别导入完成',
            'success': success_count,
            'fail': fail_count,
            'fail_msgs': fail_msgs
        })

    @action(detail=False, methods=['post'], url_path='cleanup-files')
    def cleanup_files(self, request):
        """清理drawings文件夹中的冗余文件"""
        try:
            # 获取所有有效的文件路径
            valid_files = set()
            for category in ProductCategory.objects.all():
                if category.drawing_pdf:
                    valid_files.add(category.drawing_pdf.name)
                if category.process_pdf:
                    valid_files.add(category.process_pdf.name)

            # 列出drawings目录下的所有文件
            all_files = []
            try:
                all_files = default_storage.listdir('drawings')[1]
            except Exception as e:
                return Response({'error': f'无法列出drawings目录下的文件: {str(e)}'}, status=400)

            # 找出所有正在使用的文件并保留备份文件
            deleted_files = []
            retained_files = []

            # 使用正则表达式识别备份文件模式
            backup_pattern = re.compile(r'^(.+)-\d+\.pdf$')
            random_suffix_pattern = re.compile(r'^(.+)_[a-zA-Z0-9]{7,}\.pdf$')

            # 收集所有基础文件名（无时间戳）
            base_filenames = {}
            for filepath in valid_files:
                if filepath.startswith('drawings/'):
                    filename = os.path.basename(filepath)
                    base_name = filename.rsplit('.', 1)[0]
                    base_filenames[base_name] = filename

            for file in all_files:
                full_path = f'drawings/{file}'

                # 保留当前正在使用的文件
                if full_path in valid_files:
                    retained_files.append(file)
                    continue

                # 检查是否是备份文件
                backup_match = backup_pattern.match(file)
                random_suffix_match = random_suffix_pattern.match(file)

                if backup_match:
                    base_name = backup_match.group(1)
                    # 只保留最新的一个备份文件（按文件名排序）
                    files_with_same_base = [f for f in all_files if f.startswith(base_name+'-') and f.endswith('.pdf')]
                    files_with_same_base.sort(reverse=True)  # 按时间戳降序排序

                    if len(files_with_same_base) > 1 and file != files_with_same_base[0]:
                        default_storage.delete(full_path)
                        deleted_files.append(file)
                    else:
                        retained_files.append(file)
                elif random_suffix_match:
                    # 删除带有随机后缀的文件
                    base_name = random_suffix_match.group(1)
                    default_storage.delete(full_path)
                    deleted_files.append(file)
                else:
                    # 其他不可识别的文件，保留
                    retained_files.append(file)

            return Response({
                'success': True,
                'deleted_files': deleted_files,
                'retained_files': retained_files,
                'message': f'成功清理了 {len(deleted_files)} 个冗余文件，保留了 {len(retained_files)} 个文件。'
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'])
    def upload_drawing(self, request, pk=None):
        category = self.get_object()
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '未收到文件'}, status=400)
        category.drawing_pdf = file
        category.save()
        return Response({'success': True, 'path': category.drawing_pdf.url})

    @action(detail=True, methods=['post'])
    def upload_process(self, request, pk=None):
        category = self.get_object()
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '未收到文件'}, status=400)
        category.process_pdf = file
        category.save()
        return Response({'success': True, 'path': category.process_pdf.url})

class CategoryParamViewSet(viewsets.ModelViewSet):
    queryset = CategoryParam.objects.all()
    serializer_class = CategoryParamSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['category']
    search_fields = ['name']

    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser])
    def import_category_params(self, request):
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

        required_cols = ['category_code', 'name']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)

        from .models import ProductCategory

        success_count = 0
        fail_count = 0
        fail_msgs = []

        for index, row in df.iterrows():
            try:
                # Get category by code instead of name
                category = ProductCategory.objects.filter(code=row['category_code']).first()
                if not category:
                    fail_msgs.append(f'第{index+1}行: 找不到产品类别代码: {row["category_code"]}')
                    fail_count += 1
                    continue

                # Create or update param
                param, created = CategoryParam.objects.update_or_create(
                    category=category,
                    name=row['name']
                )

                success_count += 1
            except Exception as e:
                fail_count += 1
                fail_msgs.append(f'第{index+1}行: {str(e)}')

        return Response({
            'msg': '类别参数导入完成',
            'success': success_count,
            'fail': fail_count,
            'fail_msgs': fail_msgs
        })

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_material=False)
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

    @action(detail=True, methods=['get'], url_path='full')
    def get_full_product(self, request, pk=None):
        """获取任何产品（包括物料），不过滤is_material"""
        try:
            product = get_object_or_404(Product.objects.all(), pk=pk)
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """重写检索方法，允许访问任何产品，包括物料"""
        try:
            instance = get_object_or_404(Product.objects.all(), pk=kwargs.get('pk'))
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        """重写更新方法，允许更新任何产品，包括物料"""
        try:
            # 从所有Product中获取实例，包括物料
            partial = kwargs.pop('partial', False)
            pk = kwargs.get('pk')
            instance = get_object_or_404(Product.objects.all(), pk=pk)
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
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        required_cols = ['category_code', 'param_items', 'param_values', 'price']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)
        from .models import ProductCategory, ProductParamValue, Unit

        success_count = 0
        fail_count = 0
        fail_msgs = []
        skipped_count = 0
        skipped_reasons = []
        duplicate_codes = []
        total_rows = len(df)
        processed_data = {}  # 记录处理过的产品代码和原因

        print(f"开始导入产品，总共{total_rows}行数据")

        for index, row in df.iterrows():
            try:
                print(f"处理第{index+1}行数据")

                # Get category by code
                category_code = str(row['category_code']).strip()
                category = ProductCategory.objects.filter(code=category_code).first()
                if not category:
                    error_msg = f'第{index+1}行: 找不到产品类别代码: {category_code}'
                    print(error_msg)
                    fail_msgs.append(error_msg)
                    fail_count += 1
                    continue

                # Get unit by code if provided
                unit = None
                if 'unit_code' in df.columns and not pd.isna(row['unit_code']):
                    unit_code = str(row['unit_code']).strip()
                    unit = Unit.objects.filter(code=unit_code).first()
                    if not unit:
                        error_msg = f'第{index+1}行: 找不到单位编码: {unit_code}'
                        print(error_msg)
                        fail_msgs.append(error_msg)
                        fail_count += 1
                        continue

                # 处理参数项和参数值
                param_items = row['param_items'].split(',') if not pd.isna(row['param_items']) else []
                param_values = row['param_values'].split(',') if not pd.isna(row['param_values']) else []

                if len(param_items) != len(param_values):
                    error_msg = f'第{index+1}行: 参数项和参数值数量不匹配: {len(param_items)}个参数项, {len(param_values)}个参数值'
                    print(error_msg)
                    fail_msgs.append(error_msg)
                    fail_count += 1
                    continue

                # 构建产品代码和名称
                product_code = category_code
                product_name = category.display_name

                for i in range(len(param_items)):
                    param_item = param_items[i].strip()
                    param_value = param_values[i].strip()
                    product_code += f"-{param_value}"
                    product_name += f"-{param_value}"

                # 检查产品代码是否已经存在于数据库中
                existing_product = Product.objects.filter(code=product_code).first()

                # 检查产品代码是否已经在当前导入批次中处理过了
                if product_code in processed_data:
                    skipped_reason = f'第{index+1}行: 产品代码在当前导入批次中重复: {product_code}'
                    print(skipped_reason)
                    skipped_reasons.append(skipped_reason)
                    skipped_count += 1
                    duplicate_codes.append(product_code)
                    continue

                processed_data[product_code] = {"row": index+1, "action": "新增" if not existing_product else "更新"}

                # 创建或更新产品
                is_update = False
                if existing_product:
                    is_update = True
                    product = existing_product

                # 获取价格
                price = 0
                try:
                    price = float(row['price']) if isinstance(row['price'], (int, float, str)) and row['price'] != '' else 0
                except (ValueError, TypeError) as e:
                    price = 0
                    print(f"第{index+1}行价格解析错误: {e}, 使用默认值0")

                # 创建或更新产品记录
                try:
                    product, created = Product.objects.update_or_create(
                        code=product_code,
                        defaults={
                            'name': product_name,
                            'price': price,
                            'category': category,
                            'unit': unit,
                            'is_material': False
                        }
                    )

                    if created:
                        print(f"第{index+1}行: 创建产品成功: {product_code}")
                    else:
                        print(f"第{index+1}行: 更新产品成功: {product_code}")

                    # 如果是更新操作，先删除现有的参数值
                    if not created:
                        deleted_count = ProductParamValue.objects.filter(product=product).delete()[0]
                        print(f"第{index+1}行: 删除了{deleted_count}个旧参数值")

                    # 保存参数值
                    param_success_count = 0
                    for i in range(len(param_items)):
                        param_name = param_items[i].strip()
                        param_value = param_values[i].strip()

                        # 查找或创建参数项
                        param, param_created = CategoryParam.objects.get_or_create(
                            category=category,
                            name=param_name
                        )

                        if param_created:
                            print(f"第{index+1}行: 创建参数项: {param_name}")

                        # 创建参数值
                        try:
                            param_value_obj = ProductParamValue.objects.create(
                                product=product,
                                param=param,
                                value=param_value
                            )
                            param_success_count += 1
                        except Exception as param_error:
                            print(f"第{index+1}行: 参数值 '{param_name}:{param_value}' 保存失败: {str(param_error)}")

                    print(f"第{index+1}行: 成功保存{param_success_count}/{len(param_items)}个参数值")

                    success_count += 1
                except Exception as product_error:
                    error_msg = f'第{index+1}行: 产品保存失败: {str(product_error)}'
                    print(error_msg)
                    fail_msgs.append(error_msg)
                    fail_count += 1

            except Exception as e:
                error_msg = f'第{index+1}行: 处理失败: {str(e)}'
                print(error_msg)
                fail_count += 1
                fail_msgs.append(error_msg)

        print(f"导入完成: 总共{total_rows}行, 成功{success_count}行, 失败{fail_count}行, 跳过{skipped_count}行")

        return Response({
            'msg': '导入完成',
            'total': total_rows,
            'success': success_count,
            'fail': fail_count,
            'skipped': skipped_count,
            'fail_msgs': fail_msgs,
            'skipped_reasons': skipped_reasons,
            'duplicate_codes': duplicate_codes,
            'processed_data': processed_data
        })

class ProductParamValueViewSet(viewsets.ModelViewSet):
    queryset = ProductParamValue.objects.all()
    serializer_class = ProductParamValueSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'param']
    search_fields = ['value']

    def get_queryset(self):
        queryset = ProductParamValue.objects.all()

        # 获取请求中的产品ID过滤参数
        product_id = self.request.query_params.get('product', None)

        # 如果提供了产品ID，则按产品ID过滤
        if product_id:
            try:
                product_id = int(product_id)
                queryset = queryset.filter(product_id=product_id)
                print(f"为产品ID={product_id}过滤参数值，获取到{queryset.count()}条记录")
            except (ValueError, TypeError):
                print(f"无效的产品ID: {product_id}")

        return queryset

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        批量删除指定产品的所有参数值
        POST /api/product-param-values/bulk-delete/  { "product": 123 }
        """
        product_id = request.data.get('product')
        if not product_id:
            return Response({'error': '缺少product参数'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = ProductParamValue.objects.filter(product_id=product_id).delete()
        return Response({'deleted': deleted})

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
    
    def get_object(self):
        """重写get_object方法，确保从is_material=True的查询集中获取对象"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 获取查找参数
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        
        # 从查询集中查找对象
        lookup_value = self.kwargs[lookup_url_kwarg]
        filter_kwargs = {self.lookup_field: lookup_value}
        
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        
        return obj

    def update(self, request, *args, **kwargs):
        """重写更新方法，确保正确处理物料参数值"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            # 从请求数据中分离出参数值
            data = request.data.copy()
            param_values = data.pop('param_values', [])

            # 处理字符串格式的JSON数据
            if isinstance(param_values, str):
                try:
                    param_values = json.loads(param_values)
                except Exception as e:
                    print(f"解析param_values字符串失败: {e}")
                    param_values = []

            # 处理多种可能的参数值格式
            if isinstance(param_values, list) and param_values and isinstance(param_values[0], str):
                try:
                    param_values = [json.loads(x) for x in param_values]
                except Exception as e:
                    print(f"解析param_values列表元素失败: {e}")
                    param_values = []

            if param_values and isinstance(param_values, list) and isinstance(param_values[0], list):
                param_values = [item for sublist in param_values for item in sublist]

            # 处理物料数据更新
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)

            # 处理图纸文件
            drawing_pdf = request.FILES.get('drawing_pdf', None)
            if drawing_pdf is None or (hasattr(drawing_pdf, 'size') and drawing_pdf.size == 0):
                if 'drawing_pdf' in serializer.validated_data:
                    serializer.validated_data.pop('drawing_pdf')

            # 保存物料基本信息
            material = serializer.save()

            # 删除旧的参数值并创建新的
            if param_values:
                # 删除现有参数值
                ProductParamValue.objects.filter(product=material).delete()

                # 创建新的参数值
                print(f"更新物料 {material.id} 的参数值: {param_values}")
                for pv in param_values:
                    if isinstance(pv, dict) and 'param' in pv and 'value' in pv:
                        param_id = pv.get('param')
                        value = pv.get('value')
                        print(f"创建参数值: param_id={param_id}, value={value}")
                        ProductParamValue.objects.create(
                            product=material,
                            param_id=param_id,
                            value=value
                        )

            return Response(serializer.data)
        except Exception as e:
            import traceback
            print(f"更新物料失败: {e}")
            print(traceback.format_exc())
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
        required_cols = ['code', 'name', 'price', 'category_code']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)
        from .models import ProductCategory, ProductParamValue, Unit

        success_count = 0
        fail_count = 0
        fail_msgs = []

        for index, row in df.iterrows():
            try:
                # Get category by code instead of name
                category = ProductCategory.objects.filter(code=row['category_code']).first()
                if not category:
                    fail_msgs.append(f'第{index+1}行: 找不到物料类别代码: {row["category_code"]}')
                    fail_count += 1
                    continue

                # Get unit by code if provided
                unit = None
                if 'unit_code' in df.columns and not pd.isna(row['unit_code']):
                    unit = Unit.objects.filter(code=row['unit_code']).first()
                    if not unit:
                        fail_msgs.append(f'第{index+1}行: 找不到单位编码: {row["unit_code"]}')
                    fail_count += 1
                    continue

                # Create or update material
                price = float(row['price']) if isinstance(row['price'], (int, float, str)) else 0

                # If name is empty, use category's display_name
                name = row['name']
                if pd.isna(name) or name == '':
                    name = category.display_name

                product, created = Product.objects.update_or_create(
                    code=row['code'],
                    defaults={
                        'name': name,
                        'price': price,
                        'category': category,
                        'unit': unit,
                        'is_material': True  # 确保是物料
                    }
                )

                # Process param values if included
                for col in df.columns:
                    if col in required_cols or pd.isna(row[col]):
                        continue
                    # Find param by name
                    param = CategoryParam.objects.filter(category=category, name=col).first()
                    if param:
                        # Create or update parameter value
                        ProductParamValue.objects.update_or_create(
                            product=product,
                            param=param,
                            defaults={'value': str(row[col])}
                        )

                success_count += 1
            except Exception as e:
                fail_count += 1
                fail_msgs.append(f'第{index+1}行: {str(e)}')

        return Response({
            'msg': '导入完成',
            'success': success_count,
            'fail': fail_count,
            'fail_msgs': fail_msgs
        })

class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser])
    def import_processes(self, request):
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

        required_cols = ['code', 'name']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)

        success_count = 0
        fail_count = 0
        fail_msgs = []

        for index, row in df.iterrows():
            try:
                # Create or update process
                description = row.get('description', '') if 'description' in row and not pd.isna(row['description']) else ''
                process, created = Process.objects.update_or_create(
                    code=row['code'],
                    defaults={
                        'name': row['name'],
                        'description': description
                    }
                )

                success_count += 1
            except Exception as e:
                fail_count += 1
                fail_msgs.append(f'第{index+1}行: {str(e)}')

        return Response({
            'msg': '工序导入完成',
            'success': success_count,
            'fail': fail_count,
            'fail_msgs': fail_msgs
        })

class ProcessCodeViewSet(viewsets.ModelViewSet):
    queryset = ProcessCode.objects.all()
    serializer_class = ProcessCodeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'version']

    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser])
    def import_process_codes(self, request):
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

        required_cols = ['code', 'version']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)

        success_count = 0
        fail_count = 0
        fail_msgs = []

        for index, row in df.iterrows():
            try:
                # Create or update process code
                description = row.get('description', '') if 'description' in row and not pd.isna(row['description']) else ''
                process_code, created = ProcessCode.objects.update_or_create(
                    code=row['code'],
                    version=row['version'],
                    defaults={
                        'description': description
                    }
                )

                success_count += 1
            except Exception as e:
                fail_count += 1
                fail_msgs.append(f'第{index+1}行: {str(e)}')

        return Response({
            'msg': '工艺流程导入完成',
            'success': success_count,
            'fail': fail_count,
            'fail_msgs': fail_msgs
        })

def replace_process_content_params(content, param_values: dict):
    """
    替换工艺流程明细内容中的参数表达式
    :param content: 原始内容
    :param param_values: 参数名到值的映射（字符串）
    :return: 替换后的内容
    """
    if not content:
        return content
    result = content

    # 先处理 ${param+value} 或 ${param-value}
    def expr_repl(match):
        param_name, operator, value = match.group(1), match.group(2), match.group(3)
        try:
            param_value = float(param_values.get(param_name, ''))
            op_value = float(value)
            calc = param_value + op_value if operator == '+' else param_value - op_value
            logging.debug(f"表达式替换: {param_name}{operator}{value} -> {calc}")
            return str(int(calc)) if calc.is_integer() else f"{calc:.2f}"
        except Exception as e:
            logging.warning(f"表达式替换失败: {match.group(0)}，错误: {e}")
            return match.group(0)
    result = re.sub(r'\$\{([A-Za-z0-9_]+)([+\-])(\d+(?:\.\d+)?)\}', expr_repl, result)

    # 再处理 ${param}
    def param_repl(match):
        param_name = match.group(1)
        value = param_values.get(param_name, match.group(0))
        logging.debug(f"参数替换: {param_name} -> {value}")
        return str(value)
    result = re.sub(r'\$\{([A-Za-z0-9_]+)\}', param_repl, result)

    return result

class ProductProcessCodeViewSet(viewsets.ModelViewSet):
    queryset = ProductProcessCode.objects.all()
    serializer_class = ProductProcessCodeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['product', 'process_code', 'is_default']
    search_fields = ['product__name', 'process_code__code']

    def perform_create(self, serializer):
        """创建时，如果设置为默认，则将同产品下的其他工艺流程代码设为非默认"""
        new_relation = serializer.save()
        if new_relation.is_default:
            ProductProcessCode.objects.filter(product=new_relation.product).exclude(pk=new_relation.pk).update(is_default=False)

    def perform_update(self, serializer):
        """更新时，如果设置为默认，则将同产品下的其他工艺流程代码设为非默认"""
        updated_relation = serializer.save()
        if updated_relation.is_default:
            ProductProcessCode.objects.filter(product=updated_relation.product).exclude(pk=updated_relation.pk).update(is_default=False)

    @action(detail=True, methods=['post'], url_path='auto-generate-details')
    def auto_generate_details(self, request, pk=None):
        """
        自动从产品类默认工艺流程明细复制到本产品工艺流程代码下，并做参数替换
        """
        try:
            logging.info(f"[auto_generate_details] 开始为ProductProcessCode id={pk}自动生成工艺流程明细")
            product_process_code = self.get_object()
            product = product_process_code.product
            process_code = product_process_code.process_code
            logging.info(f"[auto_generate_details] 产品ID={product.id}, 工艺流程代码ID={process_code.id}")

            # 获取产品参数值
            param_values_qs = ProductParamValue.objects.filter(product=product)
            param_values = {pv.param.name: pv.value for pv in param_values_qs}
            logging.debug(f"[auto_generate_details] 产品参数值: {param_values}")

            # 获取产品类默认工艺流程代码
            category_process_code = ProductCategoryProcessCode.objects.filter(
                category=product.category, is_default=True
            ).first()
            if not category_process_code:
                logging.error(f"[auto_generate_details] 未找到产品类默认工艺流程代码，category_id={product.category.id}")
                return Response({'error': '未找到产品类默认工艺流程代码'}, status=400)

            # 获取模板明细
            template_details = ProcessDetail.objects.filter(process_code=category_process_code.process_code).order_by('step_no')
            created_count = 0
            for detail in template_details:
                # 检查目标工艺流程下是否已存在相同step_no+step
                exists = ProcessDetail.objects.filter(
                    process_code=process_code,
                    step_no=detail.step_no,
                    step=detail.step
                ).exists()
                if exists:
                    logging.info(f"[auto_generate_details] 已存在step_no={detail.step_no}, step={detail.step_id}，跳过")
                    continue

                # 替换参数
                process_content = replace_process_content_params(detail.process_content, param_values)
                logging.debug(f"[auto_generate_details] 原内容: {detail.process_content}，替换后: {process_content}")

                # 复制明细
                ProcessDetail.objects.create(
                    process_code=process_code,
                    step_no=detail.step_no,
                    step=detail.step,
                    machine_time=detail.machine_time,
                    labor_time=detail.labor_time,
                    process_content=process_content
                )
                created_count += 1
                logging.info(f"[auto_generate_details] 创建明细: step_no={detail.step_no}, step={detail.step_id}")

            logging.info(f"[auto_generate_details] 完成，创建明细数: {created_count}")
            return Response({'success': True, 'created': created_count})
        except Exception as e:
            import traceback
            logging.error(f"[auto_generate_details] 发生异常: {e}\n{traceback.format_exc()}")
            return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

class ProcessDetailViewSet(viewsets.ModelViewSet):
    queryset = ProcessDetail.objects.all().order_by('process_code', 'step_no')
    serializer_class = ProcessDetailSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['process_code__code', 'step__name', 'step_no']

    def get_queryset(self):
        queryset = super().get_queryset()
        process_code_id = self.request.query_params.get('process_code')
        code = self.request.query_params.get('process_code__code')
        version = self.request.query_params.get('process_code__version')
        if process_code_id:
            queryset = queryset.filter(process_code_id=process_code_id)
        elif code and version:
            queryset = queryset.filter(process_code__code=code, process_code__version=version)
        elif code:
            queryset = queryset.filter(process_code__code=code)
        elif version:
            queryset = queryset.filter(process_code__version=version)
        return queryset

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
                    
                    # 获取工序内容和所需设备（如果存在）
                    process_content = row.get('process_content', '') if 'process_content' in df.columns and not pd.isna(row.get('process_content')) else ''
                    remark = row.get('remark', '') if 'remark' in df.columns and not pd.isna(row.get('remark')) else ''
                    
                    ProcessDetail.objects.update_or_create(
                        process_code=process_code_obj,
                        step_no=row['step_no'],
                        defaults={
                            'step': step_obj,
                            'machine_time': row['machine_time'],
                            'labor_time': row['labor_time'],
                            'process_content': process_content,
                            'remark': remark
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
    queryset = BOM.objects.all()
    serializer_class = BOMSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['product__name', 'product__code', 'name', 'version']

    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser])
    def import_boms(self, request):
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

        required_cols = ['product_code', 'name', 'version', 'material_code', 'quantity']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)

        success_count = 0
        fail_count = 0
        fail_msgs = []

        # Group by product, name, and version to create BOMs and their items
        grouped = df.groupby(['product_code', 'name', 'version'])

        for (product_code, bom_name, bom_version), group in grouped:
            try:
                # Find product
                product = Product.objects.filter(code=product_code, is_material=False).first()
                if not product:
                    fail_count += len(group)
                    fail_msgs.append(f'产品代码不存在或不是产品: {product_code}')
                    continue

                # Create or update BOM
                bom, created = BOM.objects.update_or_create(
                    product=product,
                    name=bom_name,
                    version=bom_version
                )

                # If updating, clear existing items
                if not created:
                    BOMItem.objects.filter(bom=bom).delete()

                # Add BOM items
                item_success = 0
                for _, row in group.iterrows():
                    try:
                        # Find material
                        material = Product.objects.filter(code=row['material_code'], is_material=True).first()
                        if not material:
                            fail_count += 1
                            fail_msgs.append(f'物料代码不存在或不是物料: {row["material_code"]}')
                            continue

                        # Create BOM item
                        quantity = float(row['quantity']) if isinstance(row['quantity'], (int, float, str)) else 0
                        remark = row.get('remark', '') if 'remark' in row and not pd.isna(row['remark']) else ''

                        BOMItem.objects.create(
                            bom=bom,
                            material=material,
                            quantity=quantity,
                            remark=remark
                        )

                        item_success += 1
                        success_count += 1
                    except Exception as e:
                        fail_count += 1
                        fail_msgs.append(f'BOM明细创建失败: {row["material_code"]} - {str(e)}')

                # If no items were added successfully, delete the BOM
                if item_success == 0 and created:
                    bom.delete()

            except Exception as e:
                fail_count += len(group)
                fail_msgs.append(f'BOM创建失败: {product_code}/{bom_name}/{bom_version} - {str(e)}')

        return Response({
            'msg': 'BOM导入完成',
            'success': success_count,
            'fail': fail_count,
            'fail_msgs': fail_msgs
        })

class BOMItemViewSet(viewsets.ModelViewSet):
    queryset = BOMItem.objects.all()
    serializer_class = BOMItemSerializer

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all().order_by('code')
    serializer_class = UnitSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'name']

    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser])
    def import_units(self, request):
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

        required_cols = ['code', 'name']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)

        success_count = 0
        fail_count = 0
        fail_msgs = []

        for index, row in df.iterrows():
            try:
                # Create or update unit
                unit, created = Unit.objects.update_or_create(
                    code=row['code'],
                    defaults={
                        'name': row['name'],
                        'description': row.get('description', '')
                    }
                )

                success_count += 1
            except Exception as e:
                fail_count += 1
                fail_msgs.append(f'第{index+1}行: {str(e)}')

        return Response({
            'msg': '单位导入完成',
            'success': success_count,
            'fail': fail_count,
            'fail_msgs': fail_msgs
        })

class ProductCategoryProcessCodeViewSet(viewsets.ModelViewSet):
    queryset = ProductCategoryProcessCode.objects.all()
    serializer_class = ProductCategoryProcessCodeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'process_code', 'is_default']
    search_fields = ['category__display_name', 'category__code', 'process_code__code']

    def perform_create(self, serializer):
        # 如果设置为默认，则将该产品类下的其他工艺流程代码设为非默认
        if serializer.validated_data.get('is_default', False):
            ProductCategoryProcessCode.objects.filter(
                category=serializer.validated_data['category'],
                is_default=True
            ).update(is_default=False)
        serializer.save()

    def perform_update(self, serializer):
        # 如果设置为默认，则将该产品类下的其他工艺流程代码设为非默认
        if serializer.validated_data.get('is_default', False):
            ProductCategoryProcessCode.objects.filter(
                category=serializer.validated_data['category'],
                is_default=True
            ).exclude(pk=serializer.instance.pk).update(is_default=False)
        serializer.save()
        
    @action(detail=False, methods=['post'], url_path='import', parser_classes=[MultiPartParser])
    def import_category_process_codes(self, request):
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

        required_cols = ['category_code', 'process_code', 'version']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)

        success_count = 0
        fail_count = 0
        fail_msgs = []

        from .models import ProductCategory, ProcessCode

        for index, row in df.iterrows():
            try:
                # 查找产品类
                category = ProductCategory.objects.filter(code=row['category_code']).first()
                if not category:
                    fail_msgs.append(f'第{index+1}行: 找不到产品类代码: {row["category_code"]}')
                    fail_count += 1
                    continue

                # 查找工艺流程代码
                process_code = ProcessCode.objects.filter(code=row['process_code'], version=row['version']).first()
                if not process_code:
                    fail_msgs.append(f'第{index+1}行: 找不到工艺流程代码: {row["process_code"]} 版本: {row["version"]}')
                    fail_count += 1
                    continue

                # 判断是否为默认
                is_default = False
                if 'is_default' in df.columns and not pd.isna(row['is_default']):
                    is_default_value = str(row['is_default']).lower()
                    is_default = is_default_value in ['true', '1', 'yes', 'y', '是', '默认']

                # 如果设置为默认，则取消该产品类下的其他默认设置
                if is_default:
                    ProductCategoryProcessCode.objects.filter(
                        category=category,
                        is_default=True
                    ).update(is_default=False)

                # 创建或更新关联
                obj, created = ProductCategoryProcessCode.objects.update_or_create(
                    category=category,
                    process_code=process_code,
                    defaults={'is_default': is_default}
                )

                success_count += 1
            except Exception as e:
                fail_count += 1
                fail_msgs.append(f'第{index+1}行: {str(e)}')

        return Response({
            'msg': '产品类工艺流程关联导入完成',
            'success': success_count,
            'fail': fail_count,
            'fail_msgs': fail_msgs
        })

class CategoryMaterialRuleViewSet(viewsets.ModelViewSet):
    """
    产品类BOM物料规则的API端点
    """
    queryset = CategoryMaterialRule.objects.all()
    serializer_class = CategoryMaterialRuleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['source_category__code', 'source_category__display_name', 'target_category__code', 'target_category__display_name']
    ordering_fields = ['id', 'source_category__code', 'target_category__code', 'created_at', 'updated_at']
    ordering = ['id']

    def get_queryset(self):
        queryset = super().get_queryset()
        source_category_id = self.request.query_params.get('source_category', None)
        if source_category_id:
            queryset = queryset.filter(source_category_id=source_category_id)
        
        target_category_id = self.request.query_params.get('target_category', None)
        if target_category_id:
            queryset = queryset.filter(target_category_id=target_category_id)
            
        return queryset

    @action(detail=True, methods=['post'])
    def generate_material(self, request, pk=None):
        """根据规则生成物料"""
        rule = self.get_object()
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({'error': '未提供产品ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
            
            # 检查产品是否属于规则的源产品类
            if product.category_id != rule.source_category_id:
                return Response(
                    {'error': f'产品不属于规则定义的源产品类 {rule.source_category}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # 获取产品的参数值
            param_values = {pv.param.name: pv.value for pv in ProductParamValue.objects.filter(product=product)}
            
            # 获取目标产品类的参数
            target_params = CategoryParam.objects.filter(category=rule.target_category)
            
            # 计算物料参数值
            material_params = {}
            for param in target_params:
                # 查找对应的表达式
                rule_param = CategoryMaterialRuleParam.objects.filter(
                    rule=rule, 
                    target_param=param
                ).first()
                
                if rule_param:
                    # 计算表达式的值
                    expression = rule_param.expression
                    # 替换表达式中的参数
                    process_content = replace_process_content_params(expression, param_values)
                    material_params[param.name] = process_content
                else:
                    # 如果没有表达式，使用默认值或空值
                    material_params[param.name] = ""
            
            # 生成物料代码，格式：产品类代码-参数1-值1-参数2-值2...
            material_code_parts = [rule.target_category.code]
            for param_name, param_value in material_params.items():
                if param_value:  # 只包含有值的参数
                    material_code_parts.append(f"{param_name}-{param_value}")
            
            material_code = "-".join(material_code_parts)
            
            # 检查物料是否已存在
            try:
                material = Material.objects.get(code=material_code)
                material_created = False
            except Material.DoesNotExist:
                # 创建新物料
                material = Material()
                material.code = material_code
                material.name = f"{rule.target_category.display_name}-{'-'.join(f'{k}-{v}' for k, v in material_params.items() if v)}"
                material.price = 0  # 默认价格
                material.category = rule.target_category
                material.unit = rule.target_category.unit  # 使用目标产品类的默认单位
                material.is_material = True
                material.save()
                # 为物料添加参数值
                for param_name, param_value in material_params.items():
                    if param_value:
                        target_param = CategoryParam.objects.filter(
                            category=rule.target_category,
                            name=param_name
                        ).first()
                        if target_param:
                            ProductParamValue.objects.create(
                                product=material,
                                param=target_param,
                                value=param_value
                            )
                material_created = True

            # 检查BOM是否已存在
            bom_name = f"{product.code}-A"
            try:
                bom = BOM.objects.get(product=product, name=bom_name)
            except BOM.DoesNotExist:
                bom = BOM.objects.create(
                    product=product,
                    name=bom_name,
                    version="A",
                    description=f"{product.name}的默认BOM"
                )

            # 添加物料到BOM
            bom_item, created = BOMItem.objects.get_or_create(
                bom=bom,
                material=material,
                defaults={'quantity': 1.0, 'remark': '自动生成'}
            )

            return Response({
                'message': '物料生成成功',
                'material': MaterialSerializer(material).data,
                'material_created': material_created,
                'bom': BOMSerializer(bom).data,
                'bom_item_created': created
            })
                
        except Product.DoesNotExist:
            return Response({'error': '产品不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return Response({
                'success': False,
                'error': str(e),
                'traceback': tb
            }, status=500)


class CategoryMaterialRuleParamViewSet(viewsets.ModelViewSet):
    """
    产品类BOM物料规则参数表达式的API端点
    """
    queryset = CategoryMaterialRuleParam.objects.all()
    serializer_class = CategoryMaterialRuleParamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['target_param__name', 'expression']
    ordering_fields = ['id', 'target_param__name']
    ordering = ['id']

    def get_queryset(self):
        queryset = super().get_queryset()
        rule_id = self.request.query_params.get('rule', None)
        if rule_id:
            queryset = queryset.filter(rule_id=rule_id)
        return queryset

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_material(request):
    """根据物料规则生成物料和BOM"""
    rule_id = request.data.get('rule_id')
    product_id = request.data.get('product_id')

    if not rule_id or not product_id:
        return Response({'error': '缺少必要参数'}, status=400)

    try:
        rule = CategoryMaterialRule.objects.get(id=rule_id)
        product = Product.objects.get(id=product_id)

        # 获取产品参数值
        product_param_values = ProductParamValue.objects.filter(product=product)
        if not product_param_values.exists():
            return Response({'error': '产品参数值为空，无法生成物料。请先保存参数值。'}, status=400)
        # 创建参数名到值的映射
        param_name_to_value = {}
        for pv in product_param_values:
            param_name_to_value[pv.param.name] = pv.value

        # 获取规则参数表达式
        rule_params = CategoryMaterialRuleParam.objects.filter(rule=rule)
        # 计算物料参数值
        material_params = {}
        for rule_param in rule_params:
            param_name = rule_param.target_param.name
            expr = rule_param.expression
            # 解析表达式
            if expr.startswith('${') and expr.endswith('}'):
                expr_content = expr[2:-1]  # 移除${}
                # 检查是否是简单参数引用
                if expr_content in param_name_to_value:
                    material_params[param_name] = param_name_to_value[expr_content]
                else:
                    # 尝试解析数学表达式
                    try:
                        # 检查是否包含加减运算
                        if '+' in expr_content or '-' in expr_content:
                            if '+' in expr_content:
                                parts = expr_content.split('+')
                                param_name_expr = parts[0].strip()
                                value_to_add = float(parts[1].strip())
                                if param_name_expr not in param_name_to_value:
                                    return Response({'error': f'表达式引用了不存在的参数: {param_name_expr}'}, status=400)
                                param_value = float(param_name_to_value[param_name_expr])
                                result = param_value + value_to_add
                                material_params[param_name] = str(int(result)) if result.is_integer() else f"{result:.2f}"
                            elif '-' in expr_content:
                                parts = expr_content.split('-')
                                param_name_expr = parts[0].strip()
                                value_to_subtract = float(parts[1].strip())
                                if param_name_expr not in param_name_to_value:
                                    return Response({'error': f'表达式引用了不存在的参数: {param_name_expr}'}, status=400)
                                param_value = float(param_name_to_value[param_name_expr])
                                result = param_value - value_to_subtract
                                material_params[param_name] = str(int(result)) if result.is_integer() else f"{result:.2f}"
                        else:
                            return Response({'error': f'未知表达式: {expr_content}'}, status=400)
                    except (ValueError, TypeError) as e:
                        return Response({'error': f'表达式解析失败: {expr_content}, 错误: {str(e)}'}, status=400)
                # end 数学表达式
            else:
                # 非表达式，直接使用
                material_params[param_name] = expr
        # --- 物料生成逻辑 ---
        # 生成物料代码 - 格式：目标产品类代码-参数名-参数值
        material_code_parts = [rule.target_category.code]
        for param_name, param_value in material_params.items():
            material_code_parts.append(f"{param_name}-{param_value}")
        material_code = "-".join(material_code_parts)

        # 检查物料是否已存在
        try:
            material = Material.objects.get(code=material_code)
            material_created = False
        except Material.DoesNotExist:
            # 创建新物料
            material = Material()
            material.code = material_code
            material.name = f"{rule.target_category.display_name}-{'-'.join(f'{k}-{v}' for k, v in material_params.items() if v)}"
            material.price = 0  # 默认价格
            material.category = rule.target_category
            material.unit = rule.target_category.unit  # 使用目标产品类的默认单位
            material.is_material = True
            material.save()
            # 为物料添加参数值
            for param_name, param_value in material_params.items():
                if param_value:
                    target_param = CategoryParam.objects.filter(
                        category=rule.target_category,
                        name=param_name
                    ).first()
                    if target_param:
                        ProductParamValue.objects.create(
                            product=material,
                            param=target_param,
                            value=param_value
                        )
                material_created = True

        # 检查BOM是否已存在
        bom_name = f"{product.code}-A"
        try:
            bom = BOM.objects.get(product=product, name=bom_name)
        except BOM.DoesNotExist:
            bom = BOM.objects.create(
                product=product,
                name=bom_name,
                version="A",
                description=f"{product.name}的默认BOM"
            )

        # 添加物料到BOM
        bom_item, created = BOMItem.objects.get_or_create(
            bom=bom,
            material=material,
            defaults={'quantity': 1.0, 'remark': '自动生成'}
        )

        return Response({
            'message': '物料生成成功',
            'material': MaterialSerializer(material).data,
            'material_created': material_created,
            'bom': BOMSerializer(bom).data,
            'bom_item_created': created
        })
        # --- end ---
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)
