from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("comments", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameModel(
                    old_name="Comment",
                    new_name="CommentModel",
                ),
                migrations.AlterModelTable(
                    name="commentmodel",
                    table="comments_comment",
                ),
            ],
        ),
    ]
