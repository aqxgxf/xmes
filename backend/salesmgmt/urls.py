from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderHealthCheckView

router = DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('order-health-check/', OrderHealthCheckView.as_view(), name='order-health-check'),
]
