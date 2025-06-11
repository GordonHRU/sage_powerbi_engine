from django.db import models
from program.models import Program
import uuid
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

class JobScheduler(models.Model):
    job_id = models.AutoField(primary_key=True)
    job_name = models.CharField(max_length=100, unique=True, db_index=True)
    program = models.ForeignKey(
        Program, 
        on_delete=models.CASCADE,
        verbose_name='Program',
        help_text='Select a program to schedule',
        related_name='scheduled_jobs',
        db_index=True
    )
    cron_expression = models.CharField(
        max_length=100,
        help_text='Cron expression for scheduling (e.g., "0 0 * * *" for daily at midnight)'
    )
    enabled = models.BooleanField(default=True, db_index=True)
    last_run_time = models.DateTimeField(null=True, blank=True, db_index=True)
    next_run_time = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.job_name

    def calculate_next_run_time(self):
        """
        Calculate the next execution time based on cron expression
        """
        try:
            trigger = CronTrigger.from_crontab(self.cron_expression)
            next_time = trigger.get_next_fire_time(None, timezone.now())
            logger.info(f"Current time: {timezone.now()}, Next run time: {next_time}")
            return next_time
        except Exception as e:
            logger.error(f"Error calculating next run time: {str(e)}")
            return None

    def save(self, *args, **kwargs):
        # Only calculate next_run_time if it's not set
        if not self.next_run_time:
            self.next_run_time = self.calculate_next_run_time()
        
        with transaction.atomic():
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Scheduled Job'
        verbose_name_plural = 'Scheduled Jobs'
        ordering = ['-created_at']
        db_table = 'job_scheduler'
        # indexes = [
        #     models.Index(fields=['enabled', 'next_run_time']),
        #     models.Index(fields=['program', 'enabled']),
        # ]

    def get_status_display(self):
        return 'Enabled' if self.enabled else 'Disabled'

class JobExecution(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('aborted', 'Aborted'),
    ]
    
    execution_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(
        JobScheduler, 
        on_delete=models.CASCADE, 
        related_name='executions',
        db_index=True
    )
    start_time = models.DateTimeField(auto_now_add=True, db_index=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='running',
        db_index=True
    )
    output = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    is_aborted = models.BooleanField(default=False, db_index=True)
    duration = models.DurationField(null=True, blank=True)

    def abort(self):
        """中止執行中的任務"""
        if self.status == 'running':
            self.status = 'aborted'
            self.is_aborted = True
            self.end_time = timezone.now()
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.job.job_name} - {self.execution_id} ({self.status})"

    class Meta:
        verbose_name = 'Job Execution'
        verbose_name_plural = 'Job Executions'
        ordering = ['-start_time']
        db_table = 'job_execution'
        # indexes = [
        #     models.Index(fields=['job', 'status']),
        #     models.Index(fields=['start_time', 'status']),
        #     models.Index(fields=['is_aborted', 'status']),
        # ]

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)
