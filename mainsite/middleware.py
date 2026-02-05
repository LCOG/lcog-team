import datetime

from django import http
from django.conf import settings


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == getattr(settings, "HEALTH_CHECK_URL", "/health/"):
            output = {
                "status": "200 OK",
                "timestamp": datetime.datetime.now().isoformat(),
            }
            return http.JsonResponse(output)
        return self.get_response(request)