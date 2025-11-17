from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response({"detail": "Internal server error"}, status=500)

    return Response(
        {"error": response.data, "status": response.status_code},
        status=response.status_code
    )
