from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("comments.api.urls")),
    path("health/", include("comments.api.health")),
]
