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

# def create_job_view(request):
#     if request.method == 'POST':
#         try:
#             # Extract form data
#             job_name = request.POST.get('jobName', '').strip()
#             program_id = request.POST.get('programId', '').strip()
#             properties_name = request.POST.get('propertiesName', '').strip()
#             trigger_frequency = request.POST.get('triggerFrequency', '').strip()
#             trigger_day = request.POST.get('triggerDay', '').strip()
#             trigger_date = request.POST.get('triggerDate', '').strip()
#             trigger_hour = request.POST.get('triggerHour', '').strip()
#             trigger_minute = request.POST.get('triggerMinute', '').strip()
            
#             # Validation
#             errors = []
#             if not job_name:
#                 errors.append('Job Name is required')
#             if not program_id:
#                 errors.append('Program ID is required')
#             if not properties_name:
#                 errors.append('Properties Name is required')
#             if not trigger_frequency:
#                 errors.append('Trigger Frequency is required')
#             if not trigger_hour or not trigger_minute:
#                 errors.append('Trigger Time is required')
                
#             # Validate hour and minute
#             try:
#                 hour = int(trigger_hour)
#                 minute = int(trigger_minute)
#                 if not (0 <= hour <= 23):
#                     errors.append('Hour must be between 0 and 23')
#                 if not (0 <= minute <= 59):
#                     errors.append('Minute must be between 0 and 59')
#             except (ValueError, TypeError):
#                 errors.append('Invalid time format')
            
#             # Validate conditional fields
#             if trigger_frequency == 'Weekly' and not trigger_day:
#                 errors.append('Trigger Day is required for weekly frequency')
#             if trigger_frequency == 'Monthly' and not trigger_date:
#                 errors.append('Trigger Date is required for monthly frequency')
            
#             # Check if program exists
#             try:
#                 program = Program.objects.get(program_id=program_id)
#             except Program.DoesNotExist:
#                 errors.append('Selected program does not exist')
#                 program = None
            
#             # Check if job name already exists
#             if JobScheduler.objects.filter(job_name=job_name).exists():
#                 errors.append('A job with this name already exists')
            
#             if errors:
#                 for error in errors:
#                     messages.error(request, error)
#                 return render(request, 'job_scheduler/create_job.html', {
#                     'form_data': request.POST
#                 })
            
#             # Generate cron expression
#             cron_expression = generate_cron_expression(
#                 trigger_frequency, trigger_day, trigger_date, hour, minute
#             )
            
#             if not cron_expression:
#                 messages.error(request, 'Failed to generate schedule expression')
#                 return render(request, 'job_scheduler/create_job.html', {
#                     'form_data': request.POST
#                 })
            
#             # Create the job
#             job = JobScheduler.objects.create(
#                 job_name=job_name,
#                 program=program,
#                 cron_expression=cron_expression,
#                 enabled=True
#             )
            
#             logger.info(f"Created new job: {job_name} with cron: {cron_expression}")
#             messages.success(request, f'Job "{job_name}" created successfully!')
#             return redirect('job_scheduler')
            
#         except Exception as e:
#             logger.error(f"Error creating job: {str(e)}")
#             messages.error(request, f'An error occurred while creating the job: {str(e)}')
#             return render(request, 'job_scheduler/create_job.html', {
#                 'form_data': request.POST
#             })
    
#     # GET request - show the form
#     return render(request, 'job_scheduler/create_job.html')

# def generate_cron_expression(frequency, day, date, hour, minute):
#     """Generate cron expression based on frequency and time parameters"""
#     try:
#         if frequency == 'Daily':
#             return f"{minute} {hour} * * *"
#         elif frequency == 'Weekly':
#             # Convert day name to number (Monday=1, Sunday=0)
#             day_mapping = {
#                 'Monday': '1', 'Tuesday': '2', 'Wednesday': '3', 'Thursday': '4',
#                 'Friday': '5', 'Saturday': '6', 'Sunday': '0'
#             }
#             day_num = day_mapping.get(day)
#             if day_num is None:
#                 return None
#             return f"{minute} {hour} * * {day_num}"
#         elif frequency == 'Monthly':
#             return f"{minute} {hour} {date} * *"
#         else:
#             return None
#     except Exception as e:
#         logger.error(f"Error generating cron expression: {str(e)}")
#         return None

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
        # Debug logging
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Request body: {request.body}")
        
        try:
            data = json.loads(request.body)
            logger.info(f"Parsed JSON data: {data}")
            
            # Validate required fields
            required_fields = ['job_name', 'program_id', 'cron_expression']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'{field} is required'
                    }, status=400)
            
            # Debug: Check what programs exist
            all_programs = Program.objects.all()
            logger.info(f"Available programs: {[(p.program_id, p.program_name) for p in all_programs]}")
            
            # Check if program exists - try both program_id and pk
            program = None
            program_id = data['program_id']
            
            # Try different ways to find the program
            try:
                # First try with program_id field
                program = Program.objects.get(program_id=program_id)
                logger.info(f"Found program by program_id: {program}")
            except Program.DoesNotExist:
                try:
                    # Try with pk (primary key)
                    program = Program.objects.get(pk=program_id)
                    logger.info(f"Found program by pk: {program}")
                except Program.DoesNotExist:
                    try:
                        # Try converting to int if it's a string
                        program = Program.objects.get(program_id=int(program_id))
                        logger.info(f"Found program by int program_id: {program}")
                    except (Program.DoesNotExist, ValueError):
                        logger.error(f"Program with ID {program_id} not found")
                        logger.error(f"Available program IDs: {list(Program.objects.values_list('program_id', flat=True))}")
                        return JsonResponse({
                            'status': 'error', 
                            'message': f'Program with ID {program_id} does not exist. Available programs: {list(Program.objects.values_list("program_id", flat=True))}'
                        }, status=400)
            
            # Check if job name already exists
            if JobScheduler.objects.filter(job_name=data['job_name']).exists():
                return JsonResponse({
                    'status': 'error', 
                    'message': 'A job with this name already exists'
                }, status=400)
            
            with transaction.atomic():
                job = JobScheduler.objects.create(
                    job_name=data['job_name'],
                    program=program,
                    cron_expression=data['cron_expression'],
                    enabled=data.get('enabled', True)
                )
            
            logger.info(f"Created new job: {data['job_name']} with cron: {data['cron_expression']}")
            return JsonResponse({
                'status': 'success', 
                'job_id': job.job_id,
                'message': f'Job "{job.job_name}" created successfully!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error', 
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
    
    else:
        return JsonResponse({
            'status': 'error', 
            'message': 'Method not allowed'
        }, status=405)

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
