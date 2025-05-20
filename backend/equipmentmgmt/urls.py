from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EquipmentViewSet,
    EquipmentMaintenanceViewSet,
    EquipmentSpareViewSet,
    EquipmentSpareInventoryViewSet
)

router = DefaultRouter()
router.register(r'equipments', EquipmentViewSet)
router.register(r'equipment-maintenances', EquipmentMaintenanceViewSet)
router.register(r'equipment-spares', EquipmentSpareViewSet)
router.register(r'equipment-spare-inventories', EquipmentSpareInventoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 