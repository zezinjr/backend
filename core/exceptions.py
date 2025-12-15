from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException

from core import messages


class ActionFailedException(APIException):
    status_code = 400
    default_detail = _('Could not perform this action, cause: %s')

    def __init__(self, cause: str):
        super().__init__(detail=self.default_detail % (cause,))


class ReportNoRecordsException(APIException):
    status_code = 400
    default_detail = _('Report no record found')


class ForeignKeyException(APIException):
    status_code = 403
    default_detail = _('Registry with dependencies and can\'t be deleted')


class InvalidPaginatedParametersException(APIException):
    status_code = 404
    default_detail = _('Paginated result not allowed')


class ExecuteQueryException(APIException):
    status_code = 400
    default_detail = _('Error executing query: %s')

    def __init__(self, cause: str):
        super().__init__(detail=self.default_detail % (cause,))


class ReleaseNotesNotFoundException(APIException):
    status_code = 404
    default_detail = messages.RELEASE_NOTES_NOT_FOUND


class ChromaConnectionException(APIException):
    status_code = 403
    default_detail = _('Connection Chroma Refused')
