from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import WorkOrder, WorkOrderProcessDetail, ProductionOrder, ProductionMaterial, ProductionLog
from .serializers import WorkOrderSerializer, WorkOrderProcessDetailSerializer, ProductionOrderSerializer, ProductionOrderDetailSerializer, ProductionMaterialSerializer, ProductionLogSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from salesmgmt.models import Order
from salesmgmt.serializers import OrderSerializer
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from basedata.models import ProcessDetail
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
        """创建工单时，如果有工艺流程代码，自动生成对应的工序明细"""
        workorder = serializer.save()
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
            
        return workorder
    
    def _generate_process_details(self, workorder):
        """根据工艺流程代码生成工单的工序明细"""
        if not workorder.process_code:
            return
        
        # 获取工艺流程代码对应的工序明细
        process_details = ProcessDetail.objects.filter(
            process_code=workorder.process_code
        ).order_by('step_no')
        
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
                plan_start = workorder.plan_start + timezone.timedelta(minutes=step_duration * (pd.step_no - 1))
                plan_end = workorder.plan_start + timezone.timedelta(minutes=step_duration * pd.step_no)
            else:
                plan_start = None
                plan_end = None
            
            # 只有第一道工序的待加工数量设为工单数量，其他工序设为0
            pending_qty = workorder.quantity if idx == 0 else 0
                
            WorkOrderProcessDetail.objects.create(
                workorder=workorder,
                step_no=pd.step_no,
                process=pd.step,
                machine_time=pd.machine_time,
                labor_time=pd.labor_time,
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
        if not workorder.process_code:
            return Response({'detail': '工单没有工艺流程代码'}, 
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

class ProductionOrderViewSet(viewsets.ModelViewSet):
    """
    生产订单视图集，提供完整的CRUD操作
    """
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'product', 'customer']
    search_fields = ['order_number', 'product__name', 'customer__name', 'notes']
    ordering_fields = ['order_number', 'created_at', 'delivery_date', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        根据查询参数过滤结果
        """
        queryset = super().get_queryset()
        
        # 按日期范围过滤
        delivery_start = self.request.query_params.get('delivery_start')
        delivery_end = self.request.query_params.get('delivery_end')
        
        if delivery_start:
            queryset = queryset.filter(delivery_date__gte=delivery_start)
        
        if delivery_end:
            queryset = queryset.filter(delivery_date__lte=delivery_end)
            
        return queryset
    
    def get_serializer_class(self):
        """
        根据操作返回不同的序列化器
        """
        if self.action == 'retrieve':
            return ProductionOrderDetailSerializer
        return ProductionOrderSerializer
    
    @api_view_exception_handler
    def list(self, request, *args, **kwargs):
        """
        重写列表方法，使用自定义响应格式
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return success_response(data=response.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
    
    @api_view_exception_handler
    def retrieve(self, request, *args, **kwargs):
        """
        重写检索方法，使用自定义响应格式
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)
    
    @api_view_exception_handler
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        重写创建方法，使用自定义响应格式
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 添加创建者信息
        instance = serializer.save(creator=request.user, updater=request.user)
        
        # 处理材料清单
        materials_data = request.data.get('materials', [])
        for material_data in materials_data:
            material_data['order'] = instance.id
            material_serializer = ProductionMaterialSerializer(data=material_data)
            if material_serializer.is_valid():
                material_serializer.save(creator=request.user, updater=request.user)
            else:
                raise serializers.ValidationError(material_serializer.errors)
        
        # 自动添加创建日志
        ProductionLog.objects.create(
            order=instance,
            title='创建生产订单',
            content=f'用户 {request.user.username} 创建了生产订单',
            log_type='info',
            operator=request.user,
            creator=request.user,
            updater=request.user
        )
        
        return success_response(
            data=self.get_serializer(instance).data,
            message='生产订单创建成功',
            status_code=status.HTTP_201_CREATED
        )
    
    @api_view_exception_handler
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        重写更新方法，使用自定义响应格式
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 添加更新者信息
        instance = serializer.save(updater=request.user)
        
        # 添加更新日志
        ProductionLog.objects.create(
            order=instance,
            title='更新生产订单',
            content=f'用户 {request.user.username} 更新了生产订单',
            log_type='info',
            operator=request.user,
            creator=request.user,
            updater=request.user
        )
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        return success_response(
            data=self.get_serializer(instance).data,
            message='生产订单更新成功'
        )
    
    @api_view_exception_handler
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法，使用自定义响应格式
        """
        instance = self.get_object()
        instance.delete()  # 使用BaseModel中的软删除方法
        
        return success_response(
            message='生产订单删除成功',
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    @api_view_exception_handler
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        更新订单状态的自定义操作
        """
        instance = self.get_object()
        status = request.data.get('status')
        
        if not status:
            return error_response(message='未提供状态值')
        
        if status not in dict(ProductionOrder.ORDER_STATUS_CHOICES):
            return error_response(message='无效的状态值')
        
        old_status = instance.get_status_display()
        instance.status = status
        instance.updater = request.user
        instance.save()
        
        # 添加状态变更日志
        ProductionLog.objects.create(
            order=instance,
            title='订单状态变更',
            content=f'订单状态从 "{old_status}" 变更为 "{instance.get_status_display()}"',
            log_type='info',
            operator=request.user,
            creator=request.user,
            updater=request.user
        )
        
        return success_response(
            data=self.get_serializer(instance).data,
            message='订单状态更新成功'
        )


class ProductionMaterialViewSet(viewsets.ModelViewSet):
    """
    生产订单材料视图集
    """
    queryset = ProductionMaterial.objects.all()
    serializer_class = ProductionMaterialSerializer
    permission_classes = [IsAuthenticated]
    
    @api_view_exception_handler
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, updater=self.request.user)
    
    @api_view_exception_handler
    def perform_update(self, serializer):
        serializer.save(updater=self.request.user)


class ProductionLogViewSet(viewsets.ModelViewSet):
    """
    生产订单日志视图集
    """
    queryset = ProductionLog.objects.all()
    serializer_class = ProductionLogSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']  # 只允许获取和创建日志，不允许修改和删除
    
    @api_view_exception_handler
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, updater=self.request.user, operator=self.request.user)
