from rest_framework import routers
from .views import OrderViewSet
from django.urls import path

router = routers.DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = router.urls
