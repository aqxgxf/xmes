from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductionOrderViewSet, ProductionMaterialViewSet, ProductionLogViewSet, WorkOrderViewSet, OrdersWithoutWorkOrderView, WorkOrderProcessDetailViewSet

router = DefaultRouter()
router.register(r'orders', ProductionOrderViewSet)
router.register(r'materials', ProductionMaterialViewSet)
router.register(r'logs', ProductionLogViewSet)
router.register(r'workorders', WorkOrderViewSet)
router.register(r'workorder-process-details', WorkOrderProcessDetailViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('orders-without-workorder/', OrdersWithoutWorkOrderView.as_view(), name='orders-without-workorder'),
]
