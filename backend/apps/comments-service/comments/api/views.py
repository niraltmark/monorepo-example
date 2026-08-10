from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from comments.api.serializers import (
    CommentCreateSerializer,
    CommentListResponseSerializer,
    CommentReadSerializer,
    CommentUpdateSerializer,
)
from comments.services.comment_service import CommentService


class CommentListCreateView(APIView):
    """
    GET  /api/v1/comments/          — list all comments (paginated)
    POST /api/v1/comments/          — create a new comment
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.comment_service = CommentService()

    def get(self, request: Request) -> Response:
        skip = int(request.query_params.get("skip", 0))
        limit = int(request.query_params.get("limit", 100))
        todo_id = request.query_params.get("todo_id")
        user_id = request.query_params.get("user_id")

        if todo_id:
            comments, total = self.comment_service.list_comments_by_todo(todo_id, skip=skip, limit=limit)
        elif user_id:
            comments, total = self.comment_service.list_comments_by_user(user_id, skip=skip, limit=limit)
        else:
            from comments.repositories.comment_repository import CommentRepository
            repo = CommentRepository()
            comments = repo.get_all(skip=skip, limit=limit)
            total = len(comments)

        data = CommentListResponseSerializer({
            "items": comments,
            "total": total,
            "skip": skip,
            "limit": limit,
        }).data
        return Response(data)

    def post(self, request: Request) -> Response:
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = self.comment_service.create_comment(
            user_id=serializer.validated_data["user_id"],
            todo_id=serializer.validated_data["todo_id"],
            body=serializer.validated_data["body"],
        )
        return Response(CommentReadSerializer(comment).data, status=status.HTTP_201_CREATED)


class CommentDetailView(APIView):
    """
    GET    /api/v1/comments/{id}/   — retrieve a comment
    PATCH  /api/v1/comments/{id}/   — update a comment's body
    DELETE /api/v1/comments/{id}/   — soft-delete a comment
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.comment_service = CommentService()

    def get(self, request: Request, comment_id: str) -> Response:
        comment = self.comment_service.get_comment(comment_id)
        return Response(CommentReadSerializer(comment).data)

    def patch(self, request: Request, comment_id: str) -> Response:
        serializer = CommentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = self.comment_service.update_comment(
            comment_id=comment_id,
            body=serializer.validated_data["body"],
        )
        return Response(CommentReadSerializer(comment).data)

    def delete(self, request: Request, comment_id: str) -> Response:
        self.comment_service.delete_comment(comment_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentsByTodoView(APIView):
    """GET /api/v1/comments/todo/{todo_id}/ — list comments for a specific todo"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.comment_service = CommentService()

    def get(self, request: Request, todo_id: str) -> Response:
        skip = int(request.query_params.get("skip", 0))
        limit = int(request.query_params.get("limit", 100))
        comments, total = self.comment_service.list_comments_by_todo(todo_id, skip=skip, limit=limit)
        data = CommentListResponseSerializer({
            "items": comments,
            "total": total,
            "skip": skip,
            "limit": limit,
        }).data
        return Response(data)


class CommentsByUserView(APIView):
    """GET /api/v1/comments/user/{user_id}/ — list comments by a specific user"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.comment_service = CommentService()

    def get(self, request: Request, user_id: str) -> Response:
        skip = int(request.query_params.get("skip", 0))
        limit = int(request.query_params.get("limit", 100))
        comments, total = self.comment_service.list_comments_by_user(user_id, skip=skip, limit=limit)
        data = CommentListResponseSerializer({
            "items": comments,
            "total": total,
            "skip": skip,
            "limit": limit,
        }).data
        return Response(data)
