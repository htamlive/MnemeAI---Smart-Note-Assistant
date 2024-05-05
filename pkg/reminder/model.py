from typing import Any
from django.db import models
from dataclasses import dataclass
from .setup_django_orm import setup_django_orm

setup_django_orm()


@dataclass
class Reminder(models.Model):
    chat_id = models.CharField(max_length=255, primary_key=True)
    id = models.IntegerField(primary_key=True)
    task_id = models.TextField(blank=True, null=True)
    state = models.CharField(
        max_length=7,
        blank=False,
        null=False,
        default="pending",
        choices=[
            "pending",
            "revoked",
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)