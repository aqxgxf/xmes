from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from basedata.views import ProductCategoryViewSet, CategoryParamViewSet, ProductViewSet, ProductParamValueViewSet, CompanyViewSet, ProcessViewSet, ProcessCodeViewSet, ProductProcessCodeViewSet, ProcessDetailViewSet, BOMViewSet, BOMItemViewSet, CustomerViewSet, MaterialViewSet, UnitViewSet
from productionmgmt.views import WorkOrderViewSet, WorkOrderProcessDetailViewSet
from salesmgmt.views import OrderViewSet
from usermgmt.views import UserViewSet, GroupViewSet, LoginViewSet, RegisterViewSet

# DRF router
router = routers.DefaultRouter()
router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'category-params', CategoryParamViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-param-values', ProductParamValueViewSet)
router.register(r'processes', ProcessViewSet)
router.register(r'process-codes', ProcessCodeViewSet)
router.register(r'product-process-codes', ProductProcessCodeViewSet)
router.register(r'process-details', ProcessDetailViewSet)
router.register(r'boms', BOMViewSet)
router.register(r'bom-items', BOMItemViewSet)
router.register(r'basedata/companies', CompanyViewSet)
router.register(r'basedata/customers', CustomerViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'units', UnitViewSet)
router.register(r'workorders', WorkOrderViewSet)
router.register(r'workorder-process-details', WorkOrderProcessDetailViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', LoginViewSet.as_view(), name='login'),
    path('api/register/', RegisterViewSet.as_view(), name='register'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 