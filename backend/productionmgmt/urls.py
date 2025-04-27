from rest_framework import routers
from .views import WorkOrderViewSet, OrdersWithoutWorkOrderView
from django.urls import path

router = routers.DefaultRouter()
router.register(r'workorders', WorkOrderViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('orders-without-workorder/', OrdersWithoutWorkOrderView.as_view(), name='orders-without-workorder'),
]
