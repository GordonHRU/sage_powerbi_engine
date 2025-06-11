from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import JobScheduler, JobExecution
from django.utils import timezone
import json

# Create your views here.
def job_scheduler_view(request):
    
    return render(request, 'job_scheduler/job_scheduler.html')

def create_job_view(request):
    return render(request, 'job_scheduler/create_job.html')

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
                'message': '任務尚未執行'
            }
            
        return JsonResponse(response_data)
    except JobScheduler.DoesNotExist:
        return JsonResponse({'error': '找不到指定的任務'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_execution_history(request, job_id):
    try:
        job = JobScheduler.objects.get(job_id=job_id)
        executions = job.executions.order_by('-start_time')[:10]  # 只返回最近10次執行
        
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
        return JsonResponse({'error': '找不到指定的任務'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
