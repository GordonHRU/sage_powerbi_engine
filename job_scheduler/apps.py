from django.apps import AppConfig
from django.conf import settings
from django.db import connection
from django.db.utils import OperationalError
import logging

logger = logging.getLogger(__name__)

class JobSchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'job_scheduler'

    def ready(self):
        if settings.SCHEDULER_AUTOSTART:
            # Check if database tables exist before initializing
            try:
                # Try a simple query to check if tables exist
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_scheduler_yourmodel';")
                    if cursor.fetchone():
                        from .scheduler import init_scheduler
                        self.scheduler = init_scheduler()
            except OperationalError:
                # Tables don't exist yet, skip initialization
                pass