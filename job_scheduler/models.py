from django.db import models
from program.models import Program

class JobScheduler(models.Model):
    job_id = models.AutoField(primary_key=True)
    job_name = models.CharField(max_length=100, unique=True)
    program_id = models.ForeignKey(Program, on_delete=models.CASCADE)
    cron_expression = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    last_run_time = models.DateTimeField(null=True, blank=True)
    next_run_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
