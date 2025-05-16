from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import WorkOrder, WorkOrderProcessDetail
from .serializers import WorkOrderSerializer, WorkOrderProcessDetailSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from salesmgmt.models import Order
from salesmgmt.serializers import OrderSerializer
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from basedata.models import ProcessDetail, ProductCategoryProcessCode, ProductProcessCode, ProductParamValue
from django.utils import timezone
from rest_framework import serializers
from utils.response import success_response, error_response, api_view_exception_handler
from utils.authentication import IsInGroup

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all().order_by('-created_at')
    serializer_class = WorkOrderSerializer

    @action(methods=['post'], detail=False, url_path='create-by-order', permission_classes=[IsAuthenticated])
    @transaction.atomic
    def create_by_order(self, request):
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({'detail': '缺少order_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 将日期转换为日期时间
        plan_start = timezone.datetime.combine(order.order_date, timezone.datetime.min.time()) if order.order_date else None
        plan_end = timezone.datetime.combine(order.plan_delivery, timezone.datetime.min.time()) if order.plan_delivery else None

        # 直接用订单主表字段创建工单
        workorder = WorkOrder.objects.create(
            workorder_no=f"WO{order.order_no}",
            order=order,
            product=order.product,
            quantity=order.quantity,
            plan_start=plan_start,
            plan_end=plan_end,
            status='draft',
            remark=f"由订单{order.order_no}自动生成"
        )
        serializer = WorkOrderSerializer(workorder)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """创建工单时，如果设置了工艺流程代码，自动生成工序明细"""
        # 保存工单
        workorder = serializer.save()
        
        # 如果设置了工艺流程代码，生成工序明细
        if workorder.process_code:
            self._generate_process_details(workorder)
        # 如果没有设置工艺流程代码但有产品信息，尝试通过产品所属的产品类获取默认工艺流程代码
        elif workorder.product:
            # 先查找产品类是否有默认工艺流程代码
            category_process = ProductCategoryProcessCode.objects.filter(
                category=workorder.product.category,
                is_default=True
            ).first()
            
            if category_process:
                # 设置工单的工艺流程代码为产品类的默认工艺流程代码
                workorder.process_code = category_process.process_code
                workorder.save(update_fields=['process_code'])
                # 生成工序明细
                self._generate_process_details(workorder)
            else:
                # 如果产品类没有默认工艺流程代码，再尝试查找产品是否有默认工艺流程代码
                product_process = ProductProcessCode.objects.filter(
                    product=workorder.product,
                    is_default=True
                ).first()
                
                if product_process:
                    workorder.process_code = product_process.process_code
                    workorder.save(update_fields=['process_code'])
                    self._generate_process_details(workorder)

        return workorder

    def perform_update(self, serializer):
        """更新工单时，如果工艺流程代码变更，更新工序明细"""
        # 获取更新前的工单对象
        old_workorder = self.get_object()
        old_process_code = old_workorder.process_code

        # 保存更新后的工单
        workorder = serializer.save()

        # 如果工艺流程代码变更了，重新生成工艺明细
        if workorder.process_code != old_process_code:
            # 先删除原有的工序明细
            WorkOrderProcessDetail.objects.filter(workorder=workorder).delete()
            # 生成新的工序明细
            self._generate_process_details(workorder)
        # 如果没有设置工艺流程代码但有产品信息，尝试通过产品所属的产品类获取默认工艺流程代码
        elif not workorder.process_code and workorder.product:
            # 先查找产品类是否有默认工艺流程代码
            category_process = ProductCategoryProcessCode.objects.filter(
                category=workorder.product.category,
                is_default=True
            ).first()
            
            if category_process:
                # 设置工单的工艺流程代码为产品类的默认工艺流程代码
                workorder.process_code = category_process.process_code
                workorder.save(update_fields=['process_code'])
                # 生成工序明细
                self._generate_process_details(workorder)
            else:
                # 如果产品类没有默认工艺流程代码，再尝试查找产品是否有默认工艺流程代码
                product_process = ProductProcessCode.objects.filter(
                    product=workorder.product,
                    is_default=True
                ).first()
                
                if product_process:
                    workorder.process_code = product_process.process_code
                    workorder.save(update_fields=['process_code'])
                    self._generate_process_details(workorder)

        return workorder

    def _generate_process_details(self, workorder):
        """根据工艺流程代码生成工单的工序明细"""
        if not workorder.process_code:
            return

        # 获取工艺流程代码对应的工序明细
        process_details = ProcessDetail.objects.filter(
            process_code=workorder.process_code
        ).order_by('step_no')

        # 获取产品的参数项和参数值
        param_values = {}
        product_params = ProductParamValue.objects.filter(product=workorder.product)
        for param in product_params:
            param_values[param.param.name] = param.value

        # 计算每道工序的时间
        if process_details.exists() and workorder.plan_start and workorder.plan_end:
            total_duration = (workorder.plan_end - workorder.plan_start).total_seconds() / 60
            total_steps = process_details.count()
            step_duration = total_duration / total_steps if total_steps > 0 else 0
        else:
            step_duration = 0

        # 创建工单工序明细
        for idx, pd in enumerate(process_details):
            # 计算每道工序的计划开始和结束时间
            if workorder.plan_start and step_duration > 0:
                plan_start = workorder.plan_start + timezone.timedelta(minutes=step_duration * idx)
                plan_end = workorder.plan_start + timezone.timedelta(minutes=step_duration * (idx + 1))
            else:
                plan_start = None
                plan_end = None

            # 只有第一道工序的待加工数量设为工单数量，其他工序设为0
            pending_qty = workorder.quantity if idx == 0 else 0

            # 处理工序内容中的参数替换
            process_content = pd.process_content
            if process_content and param_values:
                import re
                
                # 处理新格式 ${参数名+数值} 或 ${参数名-数值} 的表达式
                dollar_brace_pattern = r'\$\{([A-Za-z][A-Za-z0-9]*)([\+\-])(\d+(?:\.\d+)?)\}'
                
                def replace_dollar_brace_expr(match):
                    param_name, op, value = match.groups()
                    if param_name in param_values:
                        param_value = float(param_values[param_name])
                        value = float(value)
                        
                        if op == '+':
                            result = param_value + value
                        elif op == '-':
                            result = param_value - value
                            
                        # 格式化为两位小数，如果是整数则不显示小数点
                        if result.is_integer():
                            return str(int(result))
                        else:
                            return f"{result:.2f}"
                    return match.group(0)  # 如果找不到参数值，保留原始表达式
                
                # 替换 ${参数名+数值} 格式的表达式
                process_content = re.sub(dollar_brace_pattern, replace_dollar_brace_expr, process_content)
                
                # 替换简单的 ${参数名} 格式
                simple_dollar_brace_pattern = r'\$\{([A-Za-z][A-Za-z0-9]*)\}'
                
                def replace_simple_dollar_brace(match):
                    param_name = match.group(1)
                    if param_name in param_values:
                        return param_values[param_name]
                    return match.group(0)  # 如果找不到参数值，保留原始表达式
                
                # 替换 ${参数名} 格式的表达式
                process_content = re.sub(simple_dollar_brace_pattern, replace_simple_dollar_brace, process_content)
                
                # 保留原来的参数替换逻辑，以保证兼容性
                # 查找所有参数名（比如D和D2）
                param_names = re.findall(r'([A-Za-z][A-Za-z0-9]*)', process_content)
                
                # 去重，按长度降序排序（确保先替换D2再替换D）
                param_names = sorted(set(param_names), key=len, reverse=True)
                
                # 对每个参数名进行替换
                for param_name in param_names:
                    if param_name in param_values:
                        # 使用正则表达式确保只替换独立的参数名（避免部分匹配）
                        pattern = r'\b' + re.escape(param_name) + r'\b'
                        process_content = re.sub(pattern, param_values[param_name], process_content)
                
                # 计算表达式，例如将括号内的加减运算处理为结果值
                pattern = r'\((\d+(?:\.\d+)?)([\+\-])(\d+(?:\.\d+)?)\)'
                while re.search(pattern, process_content):
                    def replace_expr(match):
                        # 处理各种运算
                        a, op, b = match.groups()
                        a, b = float(a), float(b)
                        if op == '+':
                            result = a + b
                        elif op == '-':
                            result = a - b
                        # 格式化为两位小数，如果是整数则不显示小数点
                        if result.is_integer():
                            return str(int(result))
                        else:
                            return f"{result:.2f}"
                    
                    process_content = re.sub(pattern, replace_expr, process_content)

            WorkOrderProcessDetail.objects.create(
                workorder=workorder,
                step_no=pd.step_no,
                process=pd.step,
                machine_time=pd.machine_time,
                labor_time=pd.labor_time,
                process_content=process_content,
                plan_start_time=plan_start,
                plan_end_time=plan_end,
                pending_quantity=pending_qty,
                processed_quantity=0,
                completed_quantity=0,
                status='pending',
                program_file=pd.program_file
            )

        # 生成工艺明细后，将工单状态更新为"待打印"
        workorder.status = 'print'
        workorder.save(update_fields=['status'])

    @action(methods=['post'], detail=True, url_path='generate-process-details')
    @transaction.atomic
    def generate_process_details(self, request, pk=None):
        """手动为工单生成工序明细的接口"""
        workorder = self.get_object()

        # 检查工单状态，只有草稿状态的工单才能生成工序明细
        if workorder.status != 'draft':
            return Response({'detail': '只有草稿状态的工单才能生成工艺明细'},
                           status=status.HTTP_400_BAD_REQUEST)

        # 检查是否已有工序明细
        existing_details = WorkOrderProcessDetail.objects.filter(workorder=workorder)
        if existing_details.exists():
            return Response({'detail': '工单已有工艺明细，请先删除现有工艺明细'},
                           status=status.HTTP_400_BAD_REQUEST)

        # 检查工单是否有工艺流程代码
        if not workorder.process_code and workorder.product:
            # 如果没有工艺流程代码但有产品，尝试从产品类获取默认工艺流程代码
            category_process = ProductCategoryProcessCode.objects.filter(
                category=workorder.product.category,
                is_default=True
            ).first()
            
            if category_process:
                # 设置工单的工艺流程代码为产品类的默认工艺流程代码
                workorder.process_code = category_process.process_code
                workorder.save(update_fields=['process_code'])
            else:
                # 如果产品类没有默认工艺流程代码，尝试查找产品是否有默认工艺流程代码
                product_process = ProductProcessCode.objects.filter(
                    product=workorder.product,
                    is_default=True
                ).first()
                
                if product_process:
                    workorder.process_code = product_process.process_code
                    workorder.save(update_fields=['process_code'])
        
        # 再次检查工单是否有工艺流程代码
        if not workorder.process_code:
            return Response({'detail': '工单没有工艺流程代码，请先设置工艺流程代码或确保产品类有默认工艺流程'},
                           status=status.HTTP_400_BAD_REQUEST)

        # 生成工序明细
        self._generate_process_details(workorder)

        # 返回更新后的工单数据
        serializer = self.get_serializer(workorder)
        return Response(serializer.data)

    @action(methods=['post'], detail=True, url_path='mark-as-printed')
    @transaction.atomic
    def mark_as_printed(self, request, pk=None):
        """标记工单为已打印状态"""
        workorder = self.get_object()

        # 只有待打印状态的工单才能标记为已下达
        if workorder.status != 'print':
            return Response({'detail': '只有待打印状态的工单才能标记为已下达'},
                           status=status.HTTP_400_BAD_REQUEST)

        # 将工单状态更新为已下达
        workorder.status = 'released'
        workorder.save(update_fields=['status'])

        # 返回更新后的工单数据
        serializer = self.get_serializer(workorder)
        return Response(serializer.data)

class WorkOrderProcessDetailViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderProcessDetail.objects.all().order_by('workorder', 'step_no')
    serializer_class = WorkOrderProcessDetailSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['workorder__workorder_no', 'process__name']

    def get_queryset(self):
        queryset = super().get_queryset()
        # 支持按工单ID过滤
        workorder_id = self.request.query_params.get('workorder', None)
        if workorder_id:
            queryset = queryset.filter(workorder_id=workorder_id)
        return queryset

class OrdersWithoutWorkOrderView(APIView):
    """
    获取未被工单关联的订单列表
    """
    def get(self, request):
        # 找出未被工单关联的订单
        used_order_ids = WorkOrder.objects.exclude(order=None).values_list('order', flat=True)
        orders = Order.objects.exclude(id__in=used_order_ids)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

