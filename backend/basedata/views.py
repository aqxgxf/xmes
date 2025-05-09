import json
from rest_framework import viewsets, status, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
import pandas as pd
from django.db import transaction
from rest_framework.response import Response
from rest_framework import filters
from .models import ProductCategory, CategoryParam, Product, ProductParamValue, Company, Process, ProcessCode, ProductProcessCode, ProcessDetail, BOM, BOMItem, Customer, Material, Unit
from .serializers import ProductCategorySerializer, CategoryParamSerializer, ProductSerializer, ProductParamValueSerializer, CompanySerializer, ProcessSerializer, ProcessCodeSerializer, ProductProcessCodeSerializer, ProcessDetailSerializer, BOMSerializer, BOMItemSerializer, CustomerSerializer, MaterialSerializer, UnitSerializer
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'display_name']

    @action(detail=True, methods=['get'])
    def params(self, request, pk=None):
        params = CategoryParam.objects.filter(category_id=pk)
        page = self.paginate_queryset(params)
        if page is not None:
            serializer = CategoryParamSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CategoryParamSerializer(params, many=True)
        return Response(serializer.data)

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
        required_cols = ['category_code', 'param_items', 'param_values', 'price']
        for col in required_cols:
            if col not in df.columns:
                return Response({'msg': f'缺少字段: {col}'}, status=status.HTTP_400_BAD_REQUEST)
        from .models import ProductCategory, ProductParamValue, Unit
        
        success_count = 0
        fail_count = 0
        fail_msgs = []
        
        for index, row in df.iterrows():
            try:
                # Get category by code
                category = ProductCategory.objects.filter(code=row['category_code']).first()
                if not category:
                    fail_msgs.append(f'第{index+1}行: 找不到产品类别代码: {row["category_code"]}')
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
                
                # 处理参数项和参数值
                param_items = row['param_items'].split(',') if not pd.isna(row['param_items']) else []
                param_values = row['param_values'].split(',') if not pd.isna(row['param_values']) else []
                
                if len(param_items) != len(param_values):
                    fail_msgs.append(f'第{index+1}行: 参数项和参数值数量不匹配')
                    fail_count += 1
                    continue
                
                # 构建产品代码和名称
                product_code = row['category_code']
                product_name = category.display_name
                
                for i in range(len(param_items)):
                    param_item = param_items[i].strip()
                    param_value = param_values[i].strip()
                    product_code += f"-{param_value}"
                    product_name += f"-{param_value}"
                
                # Create or update product
                price = float(row['price']) if isinstance(row['price'], (int, float, str)) else 0
                remark = row.get('remark', '')
                
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
                
                # Save parameter values
                for i in range(len(param_items)):
                    param_name = param_items[i].strip()
                    param_value = param_values[i].strip()
                    
                    # Find param by name for this category
                    param = CategoryParam.objects.filter(category=category, name=param_name).first()
                    if not param:
                        # Create the parameter if it doesn't exist
                        param = CategoryParam.objects.create(category=category, name=param_name)
                    
                    # Create or update parameter value
                    ProductParamValue.objects.update_or_create(
                        product=product,
                        param=param,
                        defaults={'value': param_value}
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
