from django.shortcuts import render
from rest_framework import viewsets
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

# Create your views here.

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-order_date')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all().order_by('item_no')
    serializer_class = OrderItemSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        self.update_order_total(instance.order)

    def perform_update(self, serializer):
        instance = serializer.save()
        self.update_order_total(instance.order)

    def perform_destroy(self, instance):
        order = instance.order
        instance.delete()
        self.update_order_total(order)

    def update_order_total(self, order):
        total = order.items.aggregate(sum=Sum('amount'))['sum'] or 0
        order.total_amount = total
        order.save()
