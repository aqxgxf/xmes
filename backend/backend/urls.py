from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views import ProductProcessCodeViewSet, ProductCategoryProcessCodeViewSet, ProcessDetailViewSet

router = DefaultRouter()
router.register(r'product-process-codes', ProductProcessCodeViewSet)
router.register(r'category-process-codes', ProductCategoryProcessCodeViewSet)
router.register(r'process-details', ProcessDetailViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
] 