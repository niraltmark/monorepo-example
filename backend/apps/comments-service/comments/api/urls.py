from django.urls import path

from comments.api.views import (
    CommentDetailView,
    CommentListCreateView,
    CommentsByTodoView,
    CommentsByUserView,
)

urlpatterns = [
    path("comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path("comments/<str:comment_id>/", CommentDetailView.as_view(), name="comment-detail"),
    path("comments/todo/<str:todo_id>/", CommentsByTodoView.as_view(), name="comments-by-todo"),
    path("comments/user/<str:user_id>/", CommentsByUserView.as_view(), name="comments-by-user"),
]
