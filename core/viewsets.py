from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from core import models, serializers
from core.serializers import MyTokenObtainPairSerializer

# Create your views here.
class ClientViewSet(viewsets.ModelViewSet):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = models.Sale.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.SaleExpandableSerializer
        return serializers.SimpleSaleSerializer
