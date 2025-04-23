from rest_framework import routers
from .views import WorkOrderViewSet, WorkOrderDetailViewSet, WorkOrderProcessDetailViewSet

router = routers.DefaultRouter()
router.register(r'workorders', WorkOrderViewSet)
router.register(r'workorder-details', WorkOrderDetailViewSet, basename='workorderdetail')
router.register(r'workorder-process-details', WorkOrderProcessDetailViewSet)

urlpatterns = router.urls
