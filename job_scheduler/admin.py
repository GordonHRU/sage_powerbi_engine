from django.contrib import admin
from .models import JobScheduler

class JobSchedulerAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'job_name', 'created_at', 'cron_expression',)
    search_fields = ('job_name',)
    list_filter = ('cron_expression',)
    readonly_fields = ('created_at', 'updated_at', 'job_id', 'last_run_time', 'next_run_time')

admin.site.register(JobScheduler, JobSchedulerAdmin)
