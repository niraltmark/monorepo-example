
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from comments.api.serializers import (
    CommentCreateSerializer,
    CommentListResponseSerializer,
    CommentReadSerializer,
    CommentUpdateSerializer,
    PaginationQuerySerializer,
)
from comments.services.comment_service import CommentService

class CommentServiceAPIView(GenericAPIView):

    permission_classes = [AllowAny]

    def get_comment_service(self) -> CommentService:
        return CommentService()

    def get_pagination_values(self, request: Request) -> tuple[int, int]:
        serializer = PaginationQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data["skip"], serializer.validated_data["limit"]

    def list_response(
        self, comments: list, total: int, skip: int, limit: int
    ) -> Response:
        serializer = CommentListResponseSerializer(
            {
                "items": comments,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentListCreateView(CommentServiceAPIView):

    serializer_class = CommentReadSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentReadSerializer

    def get(self, request: Request) -> Response:
        skip, limit = self.get_pagination_values(request)
        todo_id = request.query_params.get("todo_id")
        user_id = request.query_params.get("user_id")
        comment_service = self.get_comment_service()

        if todo_id:
            comments, total = comment_service.list_comments_by_todo(
                todo_id, skip=skip, limit=limit
            )
        elif user_id:
            comments, total = comment_service.list_comments_by_user(
                user_id, skip=skip, limit=limit
            )
        else:
            comments, total = comment_service.list_comments(skip=skip, limit=limit)

        return self.list_response(comments, total, skip, limit)

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = self.get_comment_service().create_comment(**serializer.validated_data)
        return Response(
            CommentReadSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

class CommentDetailView(CommentServiceAPIView):

    serializer_class = CommentReadSerializer

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return CommentUpdateSerializer
        return CommentReadSerializer

    def get(self, request: Request, comment_id: str) -> Response:
        comment = self.get_comment_service().get_comment(comment_id)
        return Response(CommentReadSerializer(comment).data, status=status.HTTP_200_OK)

    def patch(self, request: Request, comment_id: str) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = self.get_comment_service().update_comment(
            comment_id=comment_id,
            **serializer.validated_data,
        )
        return Response(CommentReadSerializer(comment).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, comment_id: str) -> Response:
        self.get_comment_service().delete_comment(comment_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentsByTodoView(CommentServiceAPIView):

    serializer_class = CommentListResponseSerializer

    def get(self, request: Request, todo_id: str) -> Response:
        skip, limit = self.get_pagination_values(request)
        comments, total = self.get_comment_service().list_comments_by_todo(
            todo_id, skip=skip, limit=limit
        )
        return self.list_response(comments, total, skip, limit)

class CommentsByUserView(CommentServiceAPIView):

    serializer_class = CommentListResponseSerializer

    def get(self, request: Request, user_id: str) -> Response:
        skip, limit = self.get_pagination_values(request)
        comments, total = self.get_comment_service().list_comments_by_user(
            user_id, skip=skip, limit=limit
        )
        return self.list_response(comments, total, skip, limit)
