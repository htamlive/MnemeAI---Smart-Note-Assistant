from django.db import models
from . import setup_django_orm


from enum import Enum

class ServiceType(Enum):
    GOOGLE_TASK_API = "google_task_api"
    NOTION = "notion"

class Authz(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    service_type = models.CharField(max_length=20, choices=[(tag.value, tag.name) for tag in ServiceType])
    current_state = models.TextField(null=True)
    token = models.TextField(null=True)
    refresh_token = models.TextField(null=True)
    client_id = models.TextField(null=True)
    client_secret = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'authz'