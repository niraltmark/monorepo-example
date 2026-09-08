
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_id', models.CharField(db_index=True, max_length=36)),
                ('todo_id', models.CharField(db_index=True, max_length=36)),
                ('body', models.TextField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('deleted', 'Deleted')], default='active', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
