from rest_framework import serializers

from account import models


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=False)
    new_password = serializers.CharField(required=True)
    reset = serializers.BooleanField(required=True)


class UserRecoveryPasswordSerilizer(serializers.Serializer):
    username = serializers.CharField(required=True)


class MenuFindMenuSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=True)
    modules = serializers.HyperlinkedRelatedField(
        queryset=models.Module.objects.all(),
        view_name='module-detail',
        required=True,
        many=True
    )


class UserPermissionSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=True)
    granted = serializers.BooleanField(required=False)


class GroupPermissionSerializer(serializers.Serializer):
    group = serializers.IntegerField(required=True)
    granted = serializers.BooleanField(required=False)


class PermissionSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=False)
    group = serializers.IntegerField(required=False)
    granted = serializers.BooleanField(required=False)
    module = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)


class ModuleMenuRootParamsSerializer(serializers.Serializer):
    module = serializers.IntegerField(required=True)


class ModuleMenuReorderSerializer(serializers.Serializer):
    item_move = serializers.HyperlinkedRelatedField(
        required=True,
        view_name='modulemenu-detail',
        queryset=models.ModuleMenu.objects.all()
    )


class HasPermissionSerializer(serializers.Serializer):
    permission_name = serializers.CharField(required=True)
