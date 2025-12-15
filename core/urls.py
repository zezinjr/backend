from rest_framework import routers

from core import viewsets

router = routers.DefaultRouter()
router.register('client', viewsets.ClientViewSet)
router.register('employee', viewsets.EmployeeViewSet)
router.register('product', viewsets.ProductViewSet)
router.register('sale', viewsets.SaleViewSet)

urlpatterns = router.urls























