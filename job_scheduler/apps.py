from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class JobSchedulerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "job_scheduler"

    def ready(self):
        # if settings.SCHEDULER_AUTOSTART:
        #     from .scheduler import init_scheduler
        #     self.scheduler = init_scheduler()
        pass
