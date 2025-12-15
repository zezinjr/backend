import time

import jwt
from django.http import JsonResponse


class JWTTokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "HTTP_AUTHORIZATION" in request.META:
            token = request.META["HTTP_AUTHORIZATION"].replace("Bearer ", "")
            if token is not None and token != "null" and not token.startswith("Basic"):
                decoded = jwt.decode(token, options={"verify_signature": False})  # nosemgrep
                if decoded.get("exp") < int(time.time()):
                    return JsonResponse({"message": "Token Expired, Try login again"}, status=401)

        return self.get_response(request)
