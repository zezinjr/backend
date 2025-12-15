from rest_framework.exceptions import APIException

from account import messages


class PermissionNotAllowedException(APIException):
    status_code = 403
    default_detail = messages.PERMISSION_NOT_ALLOWED


class InvalidPasswordException(APIException):
    status_code = 405
    default_detail = messages.INVALID_PASSWORD


class InvalidCredentials(APIException):
    status_code = 400
    default_detail = messages.INVALID_CREDENTIALS


class ActionFailedException(APIException):
    status_code = 500
    default_detail = messages.EXPORT_FIELDS


class NoRecordFoundException(APIException):
    status_code = 500
    default_detail = messages.NO_RECORD_FOUND


class UserIdRequiredException(APIException):
    status_code = 400
    default_detail = messages.USER_ID_REQUIRED


class UserNotFoundException(APIException):
    status_code = 404
    default_detail = messages.USER_NOT_FOUND
