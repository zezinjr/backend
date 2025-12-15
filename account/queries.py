from django.contrib.auth import models as auth_models
from django.db.models import Exists, OuterRef, Q
from guardian import shortcuts

from account import choices, models


def get_objects(permission: str, user: int = None, group: int = None):
    _objects = []
    if user:
        if isinstance(user, models.User):
            _user = user
        else:

            _user = models.User.objects.filter(id=user).first()

        _objects = shortcuts.get_objects_for_user(_user, permission)
    if group:
        if isinstance(group, auth_models.Group):
            _group = group
        else:
            _group = auth_models.Group.objects.filter(id=group).first()

        _objects = shortcuts.get_objects_for_group(_group, permission)

    return _objects


class GroupQuerySet:
    @staticmethod
    def with_granted(**data):
        subquery = models.User.objects.filter(
            id=data['user'],
            groups=OuterRef('pk')
        ).values('id')
        return auth_models.Group.objects.annotate(
            granted=Exists(subquery)
        )


class PermissionQuerySet:
    @staticmethod
    def with_granted(**data):
        if 'user' in data:
            subquery = models.User.objects.filter(
                pk=data['user'],
                user_permissions=OuterRef('pk'),
            ).values('id')
        else:
            subquery = auth_models.Group.objects.filter(
                pk=data['group'],
                permissions=OuterRef('pk')
            ).values('id')

        return auth_models.Permission.objects.annotate(
            granted=Exists(subquery)
        ).exclude(
            Q(content_type__app_label='admin') |
            Q(codename__in=choices.OBJECT_PERMISSIONS)
        )


class ModuleMenuQuerySet:
    @staticmethod
    def available(user: int, module: str):
        return get_objects(
            permission='account.load_module_menu',
            user=user
        ).filter(
            is_active=True,
            module__description=module,
        ).values(
            'root__description',
            'menu__description',
            'menu__icon',
            'menu__route',
            'menu__font_set',
            'has_divider',
            'is_active'
        ).order_by(
            'order'
        )
