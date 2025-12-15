import re

from django.db.models import Q

from account import models
from account import serializers


def serializer_user(user, request=None):
    from account.serializers import UserAuthSerializer
    serializer = UserAuthSerializer(user, context={'request': request})
    return serializer.data


def get_user(user, request=None):
    from account.serializers import UserAuthSerializer
    serializer = UserAuthSerializer(user, context={'request': request})
    return serializer.data


def get_user_login(user, request=None):
    from account.serializers import UserLoginSerializer
    serializer = UserLoginSerializer(user, context={'request': request})
    return serializer.data


def get_custom_jwt(username):
    token_serializer = serializers.MyTokenObtainPairSerializer()
    token = token_serializer.get_token(user=username)
    return token


def get_custom_token_query(token):
    return '?%s%s%s%s%s' % ('refresh=', str(token), '&', 'access=', str(token.access_token))


def update_groups(user, saml_groups):
    groups = models.Group.objects.select_related('group_extra_fields').filter(
        Q(name__in=saml_groups)
        | Q(group_extra_fields__code__in=saml_groups)
    )

    not_in_groups = models.Group.objects.select_related('group_extra_fields').exclude(
        Q(name__in=saml_groups)
        | Q(group_extra_fields__code__in=saml_groups)
    ).values_list('id', flat=True)

    for group in groups:
        models.AccountUserGroup.objects.get_or_create(user=user, group=group)

    models.AccountUserGroup.objects.filter(user=user, group__in=not_in_groups).delete()


def create_user(user):
    target_user = models.User.objects.filter(username=user['username'])
    if target_user.exists():
        target_user.update(email=user['email'])
        target_user = target_user.first()
        saml_groups = user['user_identity'].get('groups', None)

        if saml_groups:
            update_groups(user=target_user, saml_groups=saml_groups)


def before_login(user):
    logining_user = models.User.objects.filter(username=user['username']).first()
    if logining_user:
        saml_groups = user['user_identity'].get('groups', None)

        if saml_groups:
            update_groups(user=logining_user, saml_groups=saml_groups)


def to_snake_case(input_string):
    cleaned_string = re.sub(r'[^a-zA-Z0-9\s]', '', input_string)
    snake_case_string = re.sub(r'\s+', '_', cleaned_string)

    return snake_case_string.lower()
