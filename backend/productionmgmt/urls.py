from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  WorkOrderViewSet, OrdersWithoutWorkOrderView, WorkOrderProcessDetailViewSet, WorkOrderFeedbackViewSet

router = DefaultRouter()
router.register(r'workorders', WorkOrderViewSet)
router.register(r'workorder-process-details', WorkOrderProcessDetailViewSet)
router.register(r'workorder-feedbacks', WorkOrderFeedbackViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('orders-without-workorder/', OrdersWithoutWorkOrderView.as_view(), name='orders-without-workorder'),
]
