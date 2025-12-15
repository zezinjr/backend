from django.contrib.auth import models as auth_models
from django.contrib.auth.hashers import make_password
from django.db import models as dj_models
from django.utils.translation import gettext_lazy as _
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from account import models
from account.utils import get_user_login, serializer_user
from core.serializers import SerializerBase


class UserAuthSerializerToken(SerializerBase):
    class Meta:
        model = models.User
        fields = ['id', 'username', 'name', 'is_superuser', 'url', 'email']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    @classmethod
    def get_token(cls, user):
        if isinstance(user, str):
            user = serializer_user(user)
        token = super().get_token(user)
        serializer = UserAuthSerializerToken(user, context={'request': None})
        token['user'] = serializer.data
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return {
            'token': data,
            'user': get_user_login(self.user)
        }


class SerializerBase(FlexFieldsModelSerializer, serializers.HyperlinkedModelSerializer):
    serializer_field_mapping = {
        dj_models.AutoField: serializers.IntegerField,
        dj_models.BigIntegerField: serializers.IntegerField,
        dj_models.BooleanField: serializers.BooleanField,
        dj_models.CharField: serializers.CharField,
        dj_models.CommaSeparatedIntegerField: serializers.CharField,
        dj_models.DateField: serializers.DateField,
        dj_models.DateTimeField: serializers.DateTimeField,
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


class UserAuthSerializer(SerializerBase):
    class Meta:
        model = models.User
        fields = ['id', 'username', 'name', 'is_superuser', 'url']


class UserLoginSerializer(SerializerBase):
    class Meta:
        model = models.User
        fields = ['id', 'username', 'name', 'is_superuser', 'url']


class UserSerializer(SerializerBase):
    associated = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.User
        fields = [
            'id',
            'url',
            'username',
            'name',
            'email',
            'last_login',
            'is_active',
            'is_superuser',
            'is_staff',
            'is_default',
            'associated',
            'is_privileged_user'
        ]

    def create(self, validated_data):
        if validated_data.get('password') is None:
            validated_data['password'] = make_password('123456')
        else:
            validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)


class UserListSerializer(SerializerBase):
    class Meta:
        model = models.User
        fields = '__all__'


class GroupSerializer(SerializerBase):
    granted = serializers.BooleanField(read_only=True)
    code = serializers.CharField(read_only=True)

    def validate(self, attrs):
        code = self.initial_data.get('code', None)
        if code:
            if models.GroupExtraFields.objects.filter(code=code).exists():
                raise serializers.ValidationError(_('A group with this code already exists!'))
        return super().validate(attrs)

    class Meta:
        model = auth_models.Group
        fields = '__all__'


class AccountUserGroupSerializer(SerializerBase):
    class Meta:
        model = models.AccountUserGroup
        fields = '__all__'

    expandable_fields = {
        'user': (
            'account.UserSerializer',
            {'fields': ['id', 'username']}
        ),
        'group': (
            'account.GroupSerializer',
            {'fields': ['id', 'name']}
        )
    }


class MenuSerializer(SerializerBase):
    granted = serializers.BooleanField(read_only=True)
    root_description = serializers.SlugRelatedField(read_only=True, source='root', slug_field='description')
    associated = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.Menu
        fields = '__all__'


class PermissionSerializer(SerializerBase):
    granted = serializers.BooleanField(read_only=True)
    associated = serializers.BooleanField(read_only=True)

    class Meta:
        model = auth_models.Permission
        fields = '__all__'


class ContentTypeSerializer(SerializerBase):
    class Meta:
        model = auth_models.ContentType
        fields = '__all__'


class ModuleSerializer(SerializerBase):
    description = serializers.CharField(read_only=False)
    granted = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.Module
        fields = '__all__'


class ModuleMenuSerializer(SerializerBase):
    granted = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.ModuleMenu
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=models.ModuleMenu.objects.all(),
                fields=('module', 'menu'),
                message=_('The menu has already registered for module')
            )
        ]

    expandable_fields = {
        'module': (
            'account.ModuleSerializer',
            {'fields': ['url', 'id', 'description']}
        ),
        'menu': (
            'account.MenuSerializer',
            {'fields': ['url', 'id', 'description', 'icon', 'route']}
        ),
        'root': (
            'account.MenuSerializer',
            {'fields': ['url', 'id', 'description', 'icon', 'route']}
        )
    }


class UserLightSerializer(SerializerBase):
    class Meta:
        model = models.User
        fields = ['url', 'id', 'username']


class FindAssociatedSerializerMixin(serializers.Serializer):
    target = serializers.IntegerField(required=True)


class AssociativeSerializerMixin(serializers.Serializer):
    source = serializers.IntegerField(required=True)
    target = serializers.IntegerField(required=True)
    associated = serializers.BooleanField(required=True)
