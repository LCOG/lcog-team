from django import http
from django.conf import settings

import datetime


class CorsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = settings.FRONTEND_DOMAIN
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        # response["Access-Control-Allow-Headers"] = "Accept, Accept-Encoding, Accept-Language, Access-Control-Request-Headers, Access-Control-Request-Method, Authorization, Connection, Content-Type, Host, Origin, Referer, Sec-Fetch-Dest, Sec-Fetch-Mode, Sec-Fetch-Site, User-Agent"
        response["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"
        return response


class HealthCheckMiddleware:
    def __init__(
            self, get_response
        ):
        self.get_response = get_response

    def __call__(self, request: http.HttpRequest):
        if request.path == getattr(settings, "HEALTH_CHECK_URL", "/health/"):
            output = {
                "status": "200 OK",
                "timestamp": datetime.datetime.now().isoformat(),
            }
            return http.JsonResponse(output)
        return self.get_response(request)