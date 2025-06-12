from django.contrib import admin
from .models import JobScheduler, JobExecution, Program
from django.utils.html import format_html
import logging
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone

logger = logging.getLogger(__name__)


@admin.register(JobScheduler)
class JobSchedulerAdmin(admin.ModelAdmin):
    list_display = ('job_name', 'program', 'trigger_frequency', 'cron_expression', 'enabled', 'last_run_time', 'next_run_time')
    list_filter = ('enabled', 'trigger_frequency')
    search_fields = ('job_name', 'program__program_name')
    readonly_fields = ('last_run_time', 'next_run_time', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('job_name', 'program', 'trigger_frequency', 'cron_expression', 'enabled')
        }),
        ('Timing Information', {
            'fields': ('last_run_time', 'next_run_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('executions')
    
    def save_model(self, request, obj, form, change):
        # Ensure next_run_time is calculated
        if not change or 'cron_expression' in form.changed_data:
            obj.next_run_time = obj.calculate_next_run_time()
            logger.info(f"Calculated next run time: {obj.next_run_time}")
        super().save_model(request, obj, form, change)


@admin.register(JobExecution)
class JobExecutionAdmin(admin.ModelAdmin):
    list_display = ('job', 'execution_id', 'status', 'start_time', 'end_time', 'duration', 'abort_button')
    list_filter = ('status', 'start_time')
    search_fields = ('job__job_name', 'execution_id')
    readonly_fields = ('execution_id', 'job', 'start_time', 'end_time', 'status', 'output', 'error')
    ordering = ('-start_time',)
    
    def duration(self, obj):
        if obj.end_time:
            duration = obj.end_time - obj.start_time
            return f"{duration.total_seconds():.1f} seconds"
        elif obj.status == 'running':
            duration = timezone.now() - obj.start_time
            return f"{duration.total_seconds():.1f} seconds"
        return '-'
    duration.short_description = 'Duration'
    
    def abort_button(self, obj):
        if obj.status == 'running':
            return format_html(
                '<a class="button" href="{}">Abort</a>',
                f'abort/{obj.execution_id}/'
            )
        return '-'
    abort_button.short_description = 'Actions'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'abort/<uuid:execution_id>/',
                self.admin_site.admin_view(self.abort_execution),
                name='job-execution-abort',
            ),
        ]
        return custom_urls + urls
    
    def abort_execution(self, request, execution_id):
        execution = self.get_object(request, execution_id)
        if execution and execution.abort():
            self.message_user(request, f"Job execution {execution_id} has been aborted.")
        else:
            self.message_user(request, "Failed to abort job execution.", level=messages.ERROR)
        return HttpResponseRedirect("../")