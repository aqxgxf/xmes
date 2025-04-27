from django.shortcuts import render
from rest_framework import viewsets
from .models import WorkOrder
from .serializers import WorkOrderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from salesmgmt.models import Order
from salesmgmt.serializers import OrderSerializer
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

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
        # 直接用订单主表字段创建工单
        workorder = WorkOrder.objects.create(
            workorder_no=f"WO{order.order_no}",
            order=order,
            product=order.product,
            quantity=order.quantity,
            status='draft',
            remark=f"由订单{order.order_no}自动生成"
        )
        serializer = WorkOrderSerializer(workorder)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
