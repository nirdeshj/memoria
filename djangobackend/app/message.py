from django.utils.timezone import now
from .models import Reminder
from .sse import push

def check_reminders():
    """
    This function checks all reminders in the database whose time has arrived
    and pushes them to the frontend using our SSE helper.
    """
    current_time = now()

    reminders = Reminder.objects.filter(
        time__lte=current_time,
        is_sent=False
    )

    for reminder in reminders:
        # Send data to frontend
        push(
            str(reminder.patient.id),
            {
                "title": reminder.title,
                "description": reminder.description
            }
        )

        # mark as sent so it won't repeat
        reminder.is_sent = True
        reminder.save()
