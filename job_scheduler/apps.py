from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate
import logging

logger = logging.getLogger(__name__)

class JobSchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'job_scheduler'

    def ready(self):
        if settings.SCHEDULER_AUTOSTART:
            from .scheduler import init_scheduler
            # 使用 post_migrate 信號來確保數據庫準備就緒
            post_migrate.connect(self._init_scheduler, sender=self)

    def _init_scheduler(self, sender, **kwargs):
        """在數據庫遷移完成後初始化調度器"""
        try:
            from .scheduler import init_scheduler
            self.scheduler = init_scheduler()
            logger.info("Job scheduler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize job scheduler: {str(e)}")

