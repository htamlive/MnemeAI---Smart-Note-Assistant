from typing import Any
from django.db import models

class ReminderCeleryTask(models.Model):
    REVOKED = "revoked"
    PENDING = "pending"

    choices = [(REVOKED, "revoked"), (PENDING, "pending")]

    chat_id = models.BigIntegerField()
    reminder_id = models.TextField()
    title = models.TextField(null=True)
    description = models.TextField(null=True)
    state = models.TextField(null=True)
    completed = models.BooleanField(default=False)
    due = models.DateTimeField(null=True)

    def is_cancelled(self) -> bool:
        return not self.completed and self.state == self.REVOKED

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


