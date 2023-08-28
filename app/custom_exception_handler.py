from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from py_rql.exceptions import RQLFilterParsingError

def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if isinstance(exc, RQLFilterParsingError):
        data = {
            'detail': 'Error parsing RQL query.',
            'code': 'rql_parsing_error'
        }
        response = Response(data, status=status.HTTP_400_BAD_REQUEST)

    return response
