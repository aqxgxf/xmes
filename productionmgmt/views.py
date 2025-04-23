from django.shortcuts import render
from rest_framework import viewsets
from .models import WorkOrder, WorkOrderDetail, WorkOrderProcessDetail
from .serializers import WorkOrderSerializer, WorkOrderDetailSerializer, WorkOrderProcessDetailSerializer

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all().order_by('-created_at')
    serializer_class = WorkOrderSerializer

class WorkOrderDetailViewSet(viewsets.ModelViewSet):
    serializer_class = WorkOrderDetailSerializer
    def get_queryset(self):
        queryset = WorkOrderDetail.objects.all()
        workorder_id = self.request.query_params.get('workorder')
        if workorder_id:
            queryset = queryset.filter(workorder=workorder_id)
        return queryset

class WorkOrderProcessDetailViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderProcessDetail.objects.all()
    serializer_class = WorkOrderProcessDetailSerializer

# Create your views here.
