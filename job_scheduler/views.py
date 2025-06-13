from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import JobScheduler, JobExecution
from program.models import Program
from django.utils import timezone
import json
from django.db import transaction
from static.utils.db_utils import retry_on_db_lock
import logging

logger = logging.getLogger(__name__)

def job_scheduler_view(request):
    """Display all scheduled jobs from the database"""
    jobs = JobScheduler.objects.select_related('program').all()
    context = {
        'jobs': jobs
    }
    return render(request, 'job_scheduler/job_scheduler.html', context)

@require_http_methods(["GET"])
def get_job_status(request, job_id):
    try:
        job = JobScheduler.objects.get(job_id=job_id)
        latest_execution = job.executions.order_by('-start_time').first()
        
        if latest_execution:
            response_data = {
                'job_id': job.job_id,
                'job_name': job.job_name,
                'status': latest_execution.status,
                'execution_id': str(latest_execution.execution_id),
                'start_time': latest_execution.start_time.isoformat(),
                'end_time': latest_execution.end_time.isoformat() if latest_execution.end_time else None,
                'duration': (latest_execution.end_time - latest_execution.start_time).total_seconds() if latest_execution.end_time else None,
                'output': latest_execution.output,
                'error': latest_execution.error
            }
        else:
            response_data = {
                'job_id': job.job_id,
                'job_name': job.job_name,
                'status': 'never_run',
                'message': 'Job has not been executed yet'
            }
            
        return JsonResponse(response_data)
    except JobScheduler.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_execution_history(request, job_id):
    try:
        job = JobScheduler.objects.get(job_id=job_id)
        executions = job.executions.order_by('-start_time')[:10]  # Return latest 10 executions
        
        history = []
        for execution in executions:
            history.append({
                'execution_id': str(execution.execution_id),
                'start_time': execution.start_time.isoformat(),
                'end_time': execution.end_time.isoformat() if execution.end_time else None,
                'status': execution.status,
                'duration': (execution.end_time - execution.start_time).total_seconds() if execution.end_time else None,
                'output': execution.output,
                'error': execution.error
            })
            
        return JsonResponse({'history': history})
    except JobScheduler.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@retry_on_db_lock
def create_job(request):
    """創建排程任務"""
    if request.method == 'GET':
        return render(request, 'job_scheduler/create_job.html')
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            with transaction.atomic():
                job = JobScheduler.objects.create(
                    job_name=data['job_name'],
                    program_id=data['program_id'],
                    cron_expression=data['cron_expression'],
                    enabled=data.get('enabled', True),
                    description=data.get('description', '')
                )
            return JsonResponse({'status': 'success', 'job_id': job.job_id})
        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@retry_on_db_lock
def update_job(request, job_id):
    """更新排程任務"""
    try:
        data = json.loads(request.body)
        with transaction.atomic():
            job = JobScheduler.objects.get(job_id=job_id)
            for field in ['job_name', 'program_id', 'cron_expression', 'enabled', 'description']:
                if field in data:
                    setattr(job, field, data[field])
            job.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error updating job: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@retry_on_db_lock
def delete_job(request, job_id):
    """刪除排程任務"""
    try:
        with transaction.atomic():
            job = JobScheduler.objects.get(job_id=job_id)
            job.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error deleting job: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@retry_on_db_lock
def toggle_job(request, job_id):
    """啟用/停用排程任務"""
    try:
        with transaction.atomic():
            job = JobScheduler.objects.get(job_id=job_id)
            job.enabled = not job.enabled
            job.save()
        return JsonResponse({'status': 'success', 'enabled': job.enabled})
    except Exception as e:
        logger.error(f"Error toggling job: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
