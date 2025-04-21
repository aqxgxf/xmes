from django.shortcuts import render
from rest_framework import viewsets
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-order_date')
    serializer_class = OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all().order_by('item_no')
    serializer_class = OrderItemSerializer
