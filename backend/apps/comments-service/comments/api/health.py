from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from django.urls import path

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request: Request) -> Response:
    return Response({"status": "ok", "service": "comments-service"})

urlpatterns = [
    path("", health_check, name="health"),
]
