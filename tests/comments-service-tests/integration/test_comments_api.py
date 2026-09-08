import pytest
from rest_framework.test import APIClient

from comments.models import Comment


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
def test_create_then_retrieve_comment_through_drf(api_client: APIClient) -> None:
    response = api_client.post(
        "/api/v1/comments/",
        {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "todo_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "body": "A DRF-backed comment",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["body"] == "A DRF-backed comment"
    comment_id = response.data["id"]

    response = api_client.get(f"/api/v1/comments/{comment_id}/")

    assert response.status_code == 200
    assert response.data["id"] == comment_id


@pytest.mark.django_db
def test_create_comment_rejects_invalid_uuid_and_blank_body(api_client: APIClient) -> None:
    response = api_client.post(
        "/api/v1/comments/",
        {"user_id": "not-a-uuid", "todo_id": "also-not-a-uuid", "body": "   "},
        format="json",
    )

    assert response.status_code == 400
    assert "user_id" in response.data
    assert "todo_id" in response.data
    assert "body" in response.data


@pytest.mark.django_db
def test_list_response_uses_drf_validation_and_pagination_envelope(
    api_client: APIClient,
) -> None:
    Comment.objects.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        todo_id="6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        body="First",
    )
    Comment.objects.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        todo_id="6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        body="Second",
    )

    response = api_client.get("/api/v1/comments/?skip=1&limit=1")

    assert response.status_code == 200
    assert response.data["total"] == 2
    assert response.data["skip"] == 1
    assert response.data["limit"] == 1
    assert len(response.data["items"]) == 1


@pytest.mark.django_db
def test_soft_deleted_comment_is_not_retrievable(api_client: APIClient) -> None:
    comment = Comment.objects.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        todo_id="6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        body="Will be deleted",
    )

    delete_response = api_client.delete(f"/api/v1/comments/{comment.id}/")
    get_response = api_client.get(f"/api/v1/comments/{comment.id}/")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
