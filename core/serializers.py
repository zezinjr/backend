from django.db import models as dj_models
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core import fields as core_fields
from core import models


class SerializerBase(FlexFieldsModelSerializer, serializers.HyperlinkedModelSerializer):
    serializer_field_mapping = {
        dj_models.AutoField: serializers.IntegerField,
        dj_models.BigIntegerField: serializers.IntegerField,
        dj_models.BooleanField: serializers.BooleanField,
        dj_models.CharField: serializers.CharField,
        dj_models.CommaSeparatedIntegerField: serializers.CharField,
        dj_models.DateField: serializers.DateField,
        dj_models.DateTimeField: core_fields.DateTimeFieldWithTZ,
        dj_models.DecimalField: serializers.DecimalField,
        dj_models.EmailField: serializers.EmailField,
        dj_models.Field: serializers.ModelField,
        dj_models.FileField: serializers.FileField,
        dj_models.FloatField: serializers.FloatField,
        dj_models.ImageField: serializers.ImageField,
        dj_models.IntegerField: serializers.IntegerField,
        dj_models.PositiveIntegerField: serializers.IntegerField,
        dj_models.PositiveSmallIntegerField: serializers.IntegerField,
        dj_models.SlugField: serializers.SlugField,
        dj_models.SmallIntegerField: serializers.IntegerField,
        dj_models.TextField: serializers.CharField,
        dj_models.TimeField: serializers.TimeField,
        dj_models.URLField: serializers.URLField,
        dj_models.GenericIPAddressField: serializers.IPAddressField,
        dj_models.FilePathField: serializers.FilePathField,
    }

    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)
        fields.insert(0, 'id')
        return fields


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = ['id', 'name', 'age', 'rg', 'cpf', 'active', 'modified_at']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id', 'description', 'quantity', 'active', 'modified_at']


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Employee
        fields = ['id', 'name', 'registration', 'active', 'modified_at']


class SimpleSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sale
        fields = ['id', 'product', 'client', 'employee', 'nrf', 'modified_at']


class SaleExpandableSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = models.Sale
        fields = ['id', 'product', 'client', 'employee', 'nrf', 'modified_at']
