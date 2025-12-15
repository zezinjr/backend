import reversion
from django.contrib.auth import models as auth_models
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from account import actions, exceptions, filters, mixins, models, queries, requests_serializer, serializers
from account.models import LoggedInUser
from account.serializers import MyTokenObtainPairSerializer


class AuthViewSetBase(viewsets.ModelViewSet,mixins.ViewSetExportMixin, mixins.AuthAssociativeViewSetMixin, mixins.HistoryViewSetMixin):
    _permission = None

    def __init__(self, *args, **kwargs):
        super(AuthViewSetBase, self).__init__(*args, **kwargs)
        self._permission = self.get_permission_name()

    def get_permission_name(self):
        if self.serializer_class:
            meta = self.serializer_class.Meta.model._meta
            return '{app}.view_{model}'.format(
                app=str(meta.app_label).lower(),
                model=str(meta.model_name).lower()
            )

    def options(self, request, *args, **kwargs):
        self.permission_classes = ()
        return super(AuthViewSetBase, self).options(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if request.user.has_perm(self._permission) or AllowAny in self.permission_classes:
            return super(AuthViewSetBase, self).list(request, *args, **kwargs)
        raise exceptions.PermissionNotAllowedException()

    def retrieve(self, request, *args, **kwargs):
        if request.user.has_perm(self._permission) or AllowAny in self.permission_classes:
            return super(AuthViewSetBase, self).retrieve(request, *args,
                                                         **kwargs)
        raise exceptions.PermissionNotAllowedException()

    @action(detail=True, methods=['GET'])
    def has_permission(self, request, pk, *args, **kwargs):
        rs = requests_serializer.HasPermissionSerializer(
            data=request.query_params)
        rs.is_valid(raise_exception=True)

        instance = self.get_object()
        has_permission = request.user.has_perm(
            perm=rs.validated_data.get('permission_name'),
            obj=instance
        )
        if has_permission:
            return Response(data={'detail': has_permission})
        else:
            return Response(
                data={'detail': _("You are not allowed to use module")},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['GET'], permission_classes=[AllowAny])
    def initial_module(self, request, *args, **kwargs):
        obj = serializers.ModuleSerializer(queries.get_objects(
            permission='account.load_module',
            user=request.user
        ).filter(
            is_active=True
        ).first(), many=False, context={'request': request})
        return Response(data={'detail': {'module': obj.data}})


class CustomModelViewSet(AuthViewSetBase):

    def create(self, request, *args, **kwargs):
        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(request.user)
            reversion.set_comment("CREATE")
            return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(request.user)
            reversion.set_comment("UPDATE")
            return super().update(request, *args, **kwargs)


class UserViewSet(mixins.AssociativeViewSetMixin, AuthViewSetBase):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filterset_class = filters.UserFilter
    ordering_fields = '__all__'
    ordering = ('name',)

    associate_model = 'core.DepartmentUser'
    associate_fields = ('user', 'department')

    @action(detail=True, methods=['PATCH'])
    def change_password(self, request, pk, *args, **kwargs):
        rs = requests_serializer.UserChangePasswordSerializer(
            data=request.data)
        rs.is_valid(raise_exception=True)

        instance = self.get_object()
        actions.UserActions.change_password(instance=instance,
                                            **rs.validated_data)
        return Response(data={'detail': True})

    @action(detail=False, methods=['GET'])
    def find_group_associated(self, request, *args, **kwargs):
        rs = mixins.FindAssociatedSerializerMixin(data=request.query_params)
        rs.is_valid(raise_exception=True)

        self.queryset = models.User.objects.associated(
            group=rs.validated_data['target'])
        return super(UserViewSet, self).list(request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def associate_group(self, request, *args, **kwargs):
        rs = mixins.AssociativeSerializerMixin(data=request.data)
        rs.is_valid(raise_exception=True)

        self.queryset = models.User.objects.associated(
            group=rs.validated_data['target'])
        self.queryset = self.filter_queryset(self.queryset)
        actions.UserActions.associate_to_group(queryset=self.queryset, **rs.validated_data)
        return Response(data={'detail': True})

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def recovery_password(self, request, *args, **kwargs):
        rs = requests_serializer.UserRecoveryPasswordSerilizer(
            data=request.data)
        rs.is_valid(raise_exception=True)

        data = actions.UserActions.recovery_password(**rs.validated_data)
        return Response(data=data)


class GroupViewSet(mixins.GrantPermissionViewSetMixin, AuthViewSetBase):
    queryset = models.GroupProxy.objects.code().all()
    serializer_class = serializers.GroupSerializer
    filterset_class = filters.GroupFilter
    ordering_fields = '__all__'
    ordering = ('name',)

    @staticmethod
    def granted_queryset(**kwargs):
        return queries.GroupQuerySet().with_granted(**kwargs)

    @action(detail=True, methods=['POST'])
    def grant(self, request, pk, *args, **kwargs):
        rs = requests_serializer.UserPermissionSerializer(data=request.data)
        rs.is_valid(raise_exception=True)

        instance = self.get_object()
        actions.GroupActions.grant(objects=[instance], **rs.validated_data)
        return Response(data={'detail': True})

    def update(self, request, *args, **kwargs):
        actions.GroupActions.group_extra_fields(group=self.get_object(), request=request)
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        result = super().create(request, *args, **kwargs)
        group_extra = actions.GroupActions.group_extra_fields(group=result, request=request)
        if group_extra:
            result.data['code'] = group_extra.code
        return result


class AccountGroupViewSet(AuthViewSetBase):
    queryset = models.AccountUserGroup.objects.all()
    serializer_class = serializers.AccountUserGroupSerializer
    filterset_class = filters.AccountUserGroupFilter
    ordering_fields = '__all__'
    ordering = ('id',)


class PermissionViewSet(mixins.AssociativeViewSetMixin,
                        mixins.GrantPermissionViewSetMixin,
                        AuthViewSetBase):
    queryset = auth_models.Permission.objects.all()
    serializer_class = serializers.PermissionSerializer
    filterset_class = filters.PermissionFilter
    ordering_fields = '__all__'
    ordering = ('content_type',)

    @staticmethod
    def granted_queryset(**kwargs):
        return queries.PermissionQuerySet().with_granted(**kwargs)


class ContentTypeViewSet(AuthViewSetBase):
    queryset = auth_models.ContentType.objects.exclude(app_label='admin')
    serializer_class = serializers.ContentTypeSerializer
    filterset_class = filters.ContentTypeFilter
    ordering_fields = '__all__'
    ordering = ('app_label',)


class ModuleViewSet(mixins.GrantPermissionViewSetMixin, CustomModelViewSet):
    queryset = models.Module.objects.all()
    serializer_class = serializers.ModuleSerializer
    filterset_class = filters.ModuleFilter
    ordering_fields = '__all__'
    ordering = ('-id',)

    grant_permission = 'account.load_module'
    permission_classes = ()

    @action(detail=False, methods=['GET'], permission_classes=[AllowAny])
    def with_granted(self, request, *args, **kwargs):
        return super(ModuleViewSet, self).with_granted(request, *args,
                                                       **kwargs)

    def list(self, request, *args, **kwargs):
        self.permission_classes = [AllowAny]
        return super(ModuleViewSet, self).list(request, *args, **kwargs)


class MenuViewSet(mixins.AssociativeViewSetMixin,
                  CustomModelViewSet):
    queryset = models.Menu.objects.all()
    serializer_class = serializers.MenuSerializer
    filterset_class = filters.MenuFilter
    ordering_fields = '__all__'
    ordering = ('-id',)


class ModuleMenuViewSet(mixins.AssociativeViewSetMixin,
                        mixins.GrantPermissionViewSetMixin,
                        mixins.ReorderViewSetMixin,
                        CustomModelViewSet):
    queryset = models.ModuleMenu.objects.all()
    serializer_class = serializers.ModuleMenuSerializer
    filterset_class = filters.ModuleMenuFilter
    ordering_fields = '__all__'
    ordering = ('order',)

    grant_permission = 'account.load_module_menu'

    reorder_root_field = 'module'
    reorder_child_field = 'module_menus'
    reorder_serializer_class = requests_serializer.ModuleMenuReorderSerializer

    @action(detail=False, methods=['GET'], permission_classes=[AllowAny])
    def find_menu(self, request, *args, **kwargs):
        rs = requests_serializer.MenuFindMenuSerializer(
            data=request.query_params)
        rs.is_valid(raise_exception=True)

        data = actions.ModuleMenuActions.representation(**rs.validated_data)
        return Response(data=data)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            raise exceptions.InvalidCredentials

        LoggedInUser.objects.create(user=serializer.user,
                                    last_token=serializer.validated_data['token']['access'])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
