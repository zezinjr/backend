from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated, InvalidToken, TokenError)):
        return Response(status=401)

    return response
