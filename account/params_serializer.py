from rest_framework import serializers

from account import models


class UserChangePasswordParamsSerializer(serializers.Serializer):
    password = serializers.CharField(required=False)
    new_password = serializers.CharField(required=True)
    reset = serializers.BooleanField(required=True)


class MenuFindMenuParamsSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=True)
    module = serializers.CharField(required=True)


class UserPermissionParamsSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=True)
    granted = serializers.BooleanField(required=False)


class GroupPermissionParamsSerializer(serializers.Serializer):
    group = serializers.IntegerField(required=True)
    granted = serializers.BooleanField(required=False)


class PermissionParamsSerializer(serializers.Serializer):
    user = serializers.HyperlinkedRelatedField(
        queryset=models.User.objects.all(),
        view_name='user-detail',
        required=True
    )
    codename = serializers.CharField(
        max_length=104,
        required=True
    )
