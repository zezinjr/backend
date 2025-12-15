from django.contrib.auth import models as auth_models

from account import models


def get_identity(identity):
    if isinstance(identity, models.User):
        return identity, None, None
    elif isinstance(identity, auth_models.Group):
        return None, identity, None


def get_file_from_request(context, field):
    files_request = context['request'].FILES
    if field in files_request:
        file = files_request.get(field)
        if file:
            return file.read()
    return None
