from typing import Any
from django.db import models

from pkg.model import setup_django_orm

setup_django_orm()


class ReminderCeleryTask(models.Model):
    REVOKED = "revoked"
    PENDING = "pending"

    choices = [(REVOKED, "revoked"), (PENDING, "pending")]

    chat_id = models.IntegerField()
    id = models.IntegerField()
    title = models.TextField()
    description = models.TextField()
    state = models.CharField(choices=choices, null=True)
    completed = models.BooleanField(default=False)

    def is_cancelled(self) -> bool:
        return not self.completed and self.state == self._revoked

    def mark_completed(self):
        if self.completed:
            return
        self.completed = True
        self.save()

    def revoke(self):
        if self.state == self._revoked or self.completed:
            return
        self.state = self._revoked
        self.save()

    class Meta:
        ordering = ("modified",)
