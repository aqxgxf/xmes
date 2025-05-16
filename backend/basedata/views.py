import json
from rest_framework import viewsets, status, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
import pandas as pd
from django.db import transaction
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductCategory, CategoryParam, Product, ProductParamValue, Company, Process, ProcessCode, ProductProcessCode, ProcessDetail, BOM, BOMItem, Customer, Material, Unit, ProductCategoryProcessCode
from .serializers import ProductCategorySerializer, CategoryParamSerializer, ProductSerializer, ProductParamValueSerializer, CompanySerializer, ProcessSerializer, ProcessCodeSerializer, ProductProcessCodeSerializer, ProcessDetailSerializer, BOMSerializer, BOMItemSerializer, CustomerSerializer, MaterialSerializer, UnitSerializer, ProductCategoryProcessCodeSerializer
from rest_framework import viewsets
from django.core.files.storage import default_storage
import os
import re
from rest_framework import permissions
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from openpyxl import Workbook
import io

class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all().order_by('code')
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
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
            if not file.name.endswith('.xlsx'):
                return Response({'msg': '只支持.xlsx格式文件'}, status=status.HTTP_400_BAD_REQUEST)
            
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
            if not file.name.endswith('.xlsx'):
                return Response({'msg': '只支持.xlsx格式文件'}, status=status.HTTP_400_BAD_REQUEST)
            
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
            if not file.name.endswith('.xlsx'):
                return Response({'msg': '只支持.xlsx格式文件'}, status=status.HTTP_400_BAD_REQUEST)
            
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
            if not file.name.endswith('.xlsx'):
                return Response({'msg': '只支持.xlsx格式文件'}, status=status.HTTP_400_BAD_REQUEST)
            
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
            if not file.name.endswith('.xlsx'):
                return Response({'msg': '只支持.xlsx格式文件'}, status=status.HTTP_400_BAD_REQUEST)
            
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
            if not file.name.endswith('.xlsx'):
                return Response({'msg': '只支持.xlsx格式文件'}, status=status.HTTP_400_BAD_REQUEST)
            
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

class ProductProcessCodeViewSet(viewsets.ModelViewSet):
    queryset = ProductProcessCode.objects.all()
    serializer_class = ProductProcessCodeSerializer
    permission_classes = [permissions.IsAuthenticated]
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
            if not file.name.endswith('.xlsx'):
                return Response({'msg': '只支持.xlsx格式文件'}, status=status.HTTP_400_BAD_REQUEST)
            
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
            if not file.name.endswith('.xlsx'):
                return Response({'msg': '只支持.xlsx格式文件'}, status=status.HTTP_400_BAD_REQUEST)
            
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
            if not file.name.endswith('.xlsx'):
                return Response({'msg': '只支持.xlsx格式文件'}, status=status.HTTP_400_BAD_REQUEST)
            
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
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'process_code', 'is_default']
    search_fields = ['category__display_name', 'category__code', 'process_code__code']

    def perform_create(self, serializer):
        """创建时，如果设置为默认，则将同产品类下的其他工艺流程代码设为非默认"""
        new_relation = serializer.save()
        if new_relation.is_default:
            ProductCategoryProcessCode.objects.filter(category=new_relation.category).exclude(pk=new_relation.pk).update(is_default=False)

    def perform_update(self, serializer):
        """更新时，如果设置为默认，则将同产品类下的其他工艺流程代码设为非默认"""
        updated_relation = serializer.save()
        if updated_relation.is_default:
            ProductCategoryProcessCode.objects.filter(category=updated_relation.category).exclude(pk=updated_relation.pk).update(is_default=False)
