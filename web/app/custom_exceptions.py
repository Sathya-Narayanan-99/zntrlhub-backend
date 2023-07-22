from rest_framework import status
from rest_framework.exceptions import APIException


class VisitorAlreadyReported(APIException):
    status_code = status.HTTP_208_ALREADY_REPORTED
    default_detail = 'Visitor already reported.'
    default_code = 'visitor_already_reported'