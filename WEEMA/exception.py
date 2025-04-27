from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Let DRF handle known exceptions first
    response = exception_handler(exc, context)
    
    # If response is None, this is an unhandled exception.
    if response is None:
        return Response({"error": str(exc)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if isinstance(response.data, dict):
        # Flatten nested errors
        error_messages = []
        for field, errors in response.data.items():
            if isinstance(errors, list):
                error_messages.extend([str(e) for e in errors])
            else:
                error_messages.append(str(errors))
        
        # Just take the first error message
        error_message = error_messages[0] if error_messages else "An error occurred."
        
        response.data = {"error": error_message}
    else:
        response.data = {"error": str(response.data)}
    
    return response
