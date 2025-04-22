from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.views.decorators.http import require_GET
import json
from rest_framework.routers import DefaultRouter
from .views import ProductCategoryViewSet, CategoryParamViewSet, ProductViewSet, ProductParamValueViewSet, CompanyViewSet, ProcessViewSet, ProcessCodeViewSet, ProductProcessCodeViewSet, ProcessDetailViewSet

router = DefaultRouter()

router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'category-params', CategoryParamViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-param-values', ProductParamValueViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'processes', ProcessViewSet)
router.register(r'process-codes', ProcessCodeViewSet)
router.register(r'product-process-codes', ProductProcessCodeViewSet)
router.register(r'process-details', ProcessDetailViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
