from django.shortcuts import render
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.response import api_view_exception_handler
from django.db import connections

# 创建简单的健康检查视图
class OrderHealthCheckView(APIView):
    def get(self, request):
        try:
            # 检查数据库连接
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT 1")

            # 尝试检查表是否存在
            try:
                cursor.execute("SELECT COUNT(*) FROM salesmgmt_order")
                return Response({"status": "healthy", "tables": "exist"})
            except Exception as e:
                # 表可能不存在
                return Response({
                    "status": "warning",
                    "tables": "missing",
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "Database connection failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e),
                "code": 500,
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
