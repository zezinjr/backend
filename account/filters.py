from django.contrib.auth import models as auth_models
from django.db.models import Q
from django_filters import rest_framework as filterset, widgets
from django_filters.widgets import BooleanWidget

from account import models

LIKE = 'unaccent__icontains'
EXACT = 'exact'


class CharInFilter(filterset.BaseInFilter, filterset.CharFilter):
    pass


class UserFilter(filterset.FilterSet):
    username = filterset.CharFilter(lookup_expr=LIKE)
    name = filterset.CharFilter(lookup_expr=LIKE)
    username_or_name = filterset.CharFilter(method='filter_username_name')
    is_active = filterset.BooleanFilter(widget=widgets.BooleanWidget())
    is_default = filterset.BooleanFilter(widget=widgets.BooleanWidget())

    associated = filterset.BooleanFilter(widget=widgets.BooleanWidget())

    @staticmethod
    def filter_username_name(queryset, name, value):
        return queryset.filter(Q(username__unaccent__icontains=value) | Q(
            name__unaccent__icontains=value))

    class Meta:
        model = models.User
        fields = ['username', 'name', 'username_or_name', 'is_active', 'is_default', 'associated']


class GroupFilter(filterset.FilterSet):
    name = filterset.CharFilter(lookup_expr=LIKE)
    user = filterset.NumberFilter(lookup_expr=EXACT, field_name='account_user_groups__user')

    class Meta:
        model = auth_models.Group
        fields = ['name']


class AccountUserGroupFilter(filterset.FilterSet):
    group = filterset.CharFilter(field_name='group__name', lookup_expr=LIKE)

    class Meta:
        model = models.AccountUserGroup
        fields = ['group']


class MenuFilter(filterset.FilterSet):
    description = filterset.CharFilter(lookup_expr=LIKE)
    route = filterset.CharFilter(lookup_expr=LIKE)
    module = filterset.NumberFilter(method='filter_module')
    associated = filterset.BooleanFilter(widget=BooleanWidget())
    is_root = filterset.BooleanFilter(widget=BooleanWidget(), method='filter_is_root')

    @staticmethod
    def filter_module(queryset, name, value):
        ids = models.ModuleMenu.objects.filter(
            module__id=value
        ).values_list('menu__id', flat=True)

        return queryset.filter(~Q(id__in=ids))

    @staticmethod
    def filter_is_root(queryset, name, value):
        return queryset.filter(Q(route__isnull=value))

    class Meta:
        model = models.Menu
        fields = ['description', 'route', 'associated', 'is_root']


class PermissionFilter(filterset.FilterSet):
    codename = filterset.CharFilter(lookup_expr=LIKE)
    name = filterset.CharFilter(lookup_expr=LIKE)
    codename_or_name = filterset.CharFilter(method='filter_codename_name')
    content_type = filterset.NumberFilter(lookup_expr=EXACT)
    associated = filterset.BooleanFilter(widget=BooleanWidget())
    granted = filterset.BooleanFilter(widget=widgets.BooleanWidget())

    @staticmethod
    def filter_codename_name(queryset, name, value):
        return queryset.filter(Q(codename__icontains=value) | Q(name__icontains=value))

    class Meta:
        model = auth_models.Permission
        fields = ['codename', 'name', 'codename_or_name', 'content_type', 'associated', 'granted']


class ContentTypeFilter(filterset.FilterSet):
    app_label_in = CharInFilter(lookup_expr='in', field_name='app_label')
    app_label = filterset.CharFilter(lookup_expr=LIKE)
    model = filterset.CharFilter(lookup_expr=LIKE)
    app_label_or_model = filterset.CharFilter(method='filter_app_label_model')
    app_label_not_in = CharInFilter(lookup_expr='in', field_name='model',
                                    exclude=True)

    @staticmethod
    def filter_app_label_model(queryset, name, value):
        return queryset.filter(Q(app_label__unaccent__icontains=value) | Q(
            model__unaccent__icontains=value))

    class Meta:
        model = auth_models.ContentType
        fields = ['app_label_in', 'app_label', 'model', 'app_label_or_model',
                  'app_label_not_in']


class ModuleMenuFilter(filterset.FilterSet):
    module = filterset.NumberFilter(lookup_expr=EXACT)
    module_description = filterset.CharFilter(lookup_expr=LIKE,
                                              field_name='module__description')
    menu = filterset.NumberFilter(lookup_expr=EXACT)
    menu_description = filterset.CharFilter(lookup_expr=LIKE,
                                            field_name='menu__description')
    root = filterset.NumberFilter(lookup_expr=EXACT)
    is_root = filterset.BooleanFilter(widget=BooleanWidget(),
                                      method='filter_is_root')
    root_or_menu_description = filterset.CharFilter(
        method='filter_root_menu_description')
    granted = filterset.BooleanFilter(widget=widgets.BooleanWidget())
    is_active = filterset.BooleanFilter(widget=widgets.BooleanWidget())

    @staticmethod
    def filter_is_root(queryset, name, value):
        return queryset.filter(Q(root__isnull=value))

    @staticmethod
    def filter_root_menu_description(queryset, name, value):
        return queryset.filter(
            Q(root__description__icontains=value) | Q(menu__description__icontains=value))

    class Meta:
        model = models.ModuleMenu
        fields = [
            'module',
            'module_description',
            'menu',
            'menu_description',
            'root',
            'root_or_menu_description',
            'granted',
            'is_active'
        ]


class ModuleFilter(filterset.FilterSet):
    description = filterset.CharFilter(lookup_expr=LIKE)
    is_active = filterset.BooleanFilter(widget=widgets.BooleanWidget())
    granted = filterset.BooleanFilter(widget=widgets.BooleanWidget())

    class Meta:
        model = models.Module
        fields = ['description', 'is_active', 'granted']
