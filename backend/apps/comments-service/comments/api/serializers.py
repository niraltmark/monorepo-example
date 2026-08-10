from rest_framework import serializers

from comments.models import Comment


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
    user_id = serializers.CharField(max_length=36)
    todo_id = serializers.CharField(max_length=36)
    body = serializers.CharField(min_length=1, max_length=5000)


class CommentUpdateSerializer(serializers.Serializer):
    body = serializers.CharField(min_length=1, max_length=5000)


class CommentListResponseSerializer(serializers.Serializer):
    items = CommentReadSerializer(many=True)
    total = serializers.IntegerField()
    skip = serializers.IntegerField()
    limit = serializers.IntegerField()
