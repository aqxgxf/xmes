from rest_framework import routers
from .views import WorkOrderViewSet, OrdersWithoutWorkOrderView, WorkOrderProcessDetailViewSet
from django.urls import path

router = routers.DefaultRouter()
router.register(r'workorders', WorkOrderViewSet)
router.register(r'workorder-process-details', WorkOrderProcessDetailViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('orders-without-workorder/', OrdersWithoutWorkOrderView.as_view(), name='orders-without-workorder'),
]
