from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.views.decorators.http import require_GET
import json
from rest_framework.routers import DefaultRouter
from .views import ProductCategoryViewSet, CategoryParamViewSet, ProductViewSet, ProductParamValueViewSet, CompanyViewSet, ProcessViewSet, ProcessCodeViewSet, ProductProcessCodeViewSet, ProcessDetailViewSet, BOMViewSet, BOMItemViewSet, CustomerViewSet, MaterialViewSet, UnitViewSet, ProductCategoryProcessCodeViewSet, CategoryMaterialRuleViewSet, CategoryMaterialRuleParamViewSet, generate_material

router = DefaultRouter()

router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'category-params', CategoryParamViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-param-values', ProductParamValueViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'processes', ProcessViewSet)
router.register(r'process-codes', ProcessCodeViewSet)
router.register(r'product-process-codes', ProductProcessCodeViewSet)
router.register(r'category-process-codes', ProductCategoryProcessCodeViewSet)
router.register(r'process-details', ProcessDetailViewSet)
router.register(r'boms', BOMViewSet)
router.register(r'bom-items', BOMItemViewSet)
router.register(r'units', UnitViewSet)
router.register(r'category-material-rules', CategoryMaterialRuleViewSet)
router.register(r'category-material-rule-params', CategoryMaterialRuleParamViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-material/', generate_material, name='generate-material'),
]
