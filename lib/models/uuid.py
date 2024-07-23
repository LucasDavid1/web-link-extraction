from uuid import uuid4
from django.db.models import DateTimeField, Model, UUIDField


class UUIDModel(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["created_at"]
        get_latest_by = "created_at"
