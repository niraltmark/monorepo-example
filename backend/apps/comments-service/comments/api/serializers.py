from rest_framework import serializers

from comments.comment_model import Comment

class PaginationQuerySerializer(serializers.Serializer):

    skip = serializers.IntegerField(required=False, default=0, min_value=0)
    limit = serializers.IntegerField(required=False, default=100, min_value=1, max_value=500)

class CommentReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            "id",
            "user_id",
            "todo_id",
            "body",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

class CommentCreateSerializer(serializers.Serializer):

    user_id = serializers.UUIDField()
    todo_id = serializers.UUIDField()
    body = serializers.CharField(min_length=1, max_length=5000, trim_whitespace=True)

    def validate_body(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Comment body cannot be empty.")
        return value

class CommentUpdateSerializer(serializers.Serializer):

    body = serializers.CharField(min_length=1, max_length=5000, trim_whitespace=True)

    def validate_body(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Comment body cannot be empty.")
        return value

class CommentListResponseSerializer(serializers.Serializer):

    items = CommentReadSerializer(many=True)
    total = serializers.IntegerField(min_value=0)
    skip = serializers.IntegerField(min_value=0)
    limit = serializers.IntegerField(min_value=1)
