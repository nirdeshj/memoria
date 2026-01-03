from django.db import models
import uuid

class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    age = models.IntegerField()

    def __str__(self):
        return self.name


class Reminder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    time = models.DateTimeField()
    repeat_weekly = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.patient.name})"
