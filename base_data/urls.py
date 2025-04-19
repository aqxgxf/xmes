from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.views.decorators.http import require_GET
import json
from rest_framework.routers import DefaultRouter
from .views import ProductCategoryViewSet, CategoryParamViewSet, ProductViewSet, ProductParamValueViewSet

router = DefaultRouter()

router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'category-params', CategoryParamViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-param-values', ProductParamValueViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
