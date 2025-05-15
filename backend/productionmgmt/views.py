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

