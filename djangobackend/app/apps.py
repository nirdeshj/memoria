from django.apps import AppConfig
import threading
import time

class AppConfig(AppConfig):
    name = 'app'
    def ready(self):
        from .message import check_reminders

        def run_scheduler():
            while True:
                check_reminders()
                time.sleep(30)  # check every 30 seconds

        t = threading.Thread(target=run_scheduler)
        t.daemon = True
        t.start()

