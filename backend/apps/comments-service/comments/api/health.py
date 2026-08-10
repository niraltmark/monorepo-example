from django.http import JsonResponse
from django.urls import path


def health_check(request):
    return JsonResponse({"status": "ok", "service": "Comments Service"})


urlpatterns = [
    path("", health_check, name="health"),
]
