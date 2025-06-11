from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone
from .models import JobScheduler, JobExecution
from program.models import Program
import logging
import subprocess
import os
import json
from datetime import datetime
import time

logger = logging.getLogger(__name__)

def calculate_next_run_time(cron_expression):
    """
    Calculate the next execution time based on cron expression
    """
    try:
        trigger = CronTrigger.from_crontab(cron_expression)
        return trigger.get_next_fire_time(None, timezone.now())
    except Exception as e:
        logger.error(f"Error calculating next run time: {str(e)}")
        return None

def execute_powerbi_engine(program, execution_id):
    """
    Execute Power BI Engine script with timeout
    """
    try:
        # 設置超時時間（1小時）
        timeout = 3600
        start_time = time.time()
        
        # 構建程式參數
        program_params = {
            'workspace_id': program.workspace_id,
            'report_name': program.report_name,
            'dataset_id': program.dataset_id,
            'method': program.method,
            'output_name': program.output_name,
            'output_type': program.output_type,
            'sharepoint_site': program.sharepoint_site,
            'sharepoint_path': program.sharepoint_path,
            'filelocation': program.filelocation,
            'execution_id': str(execution_id)
        }
        
        # Build command
        script_path = os.path.join('scripts', 'power_bi_engine.py')
        command = [
            'python',
            script_path,
            '--program', json.dumps(program_params, ensure_ascii=False)
        ]
        
        # Execute command with timeout
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # 即時讀取輸出
        output = []
        error = []
        
        while True:
            # 檢查是否超時
            if time.time() - start_time > timeout:
                process.kill()
                return False, "Execution timed out (over 1 hour)."
            
            # 讀取輸出
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()
            
            if stdout_line:
                output.append(stdout_line.strip())
            if stderr_line:
                error.append(stderr_line.strip())
            
            # 檢查進程是否結束
            if process.poll() is not None:
                break
            
            # 短暫休息以避免 CPU 過度使用
            time.sleep(0.1)
        
        # 獲取剩餘輸出
        remaining_stdout, remaining_stderr = process.communicate()
        if remaining_stdout:
            output.extend(remaining_stdout.splitlines())
        if remaining_stderr:
            error.extend(remaining_stderr.splitlines())
        
        stdout_str = '\n'.join(output)
        stderr_str = '\n'.join(error)
        
        # 更新執行記錄
        execution = JobExecution.objects.get(execution_id=execution_id)
        execution.output = stdout_str
        execution.error = stderr_str
        execution.status = 'completed' if process.returncode == 0 else 'failed'
        execution.end_time = timezone.now()
        execution.save()
        
        if process.returncode == 0:
            logger.info(f"Power BI Engine execution successful: {program.program_name}")
            logger.debug(f"Output: {stdout_str}")
            return True, stdout_str or "Execution completed successfully"
        else:
            logger.error(f"Power BI Engine execution failed: {program.program_name}")
            logger.error(f"Error: {stderr_str}")
            return False, stderr_str or "Unknown error occurred"
            
    except Exception as e:
        logger.error(f"Error executing Power BI Engine: {str(e)}")
        return False, str(e) or "Unknown error occurred"

def execute_job(job_id):
    try:
        job = JobScheduler.objects.get(job_id=job_id)
        program = job.program  # Get Program object
        
        # Create execution record
        execution = JobExecution.objects.create(job=job)
        
        try:
            # Update last run time
            job.last_run_time = timezone.now()
            # Calculate and update next run time
            job.next_run_time = job.calculate_next_run_time()
            job.save()
            
            # Execute task
            success, message = execute_powerbi_engine(program, execution.execution_id)
            
            # Update execution record
            execution.end_time = timezone.now()
            execution.status = 'completed' if success else 'failed'
            execution.output = message if success else ''
            execution.error = '' if success else message
            execution.save()
            
            logger.info(f"Job execution: {job.job_name} - {'Success' if success else 'Failed'}")
            
        except Exception as e:
            # Update execution record as failed
            execution.end_time = timezone.now()
            execution.status = 'failed'
            execution.error = str(e)
            execution.save()
            raise
            
    except JobScheduler.DoesNotExist:
        logger.error(f"Job not found with ID: {job_id}")
    except Exception as e:
        logger.error(f"Job execution failed: {str(e)}")

def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # Load all enabled jobs from database
    jobs = JobScheduler.objects.filter(enabled=True)
    for job in jobs:
        try:
            # Calculate and update next run time
            job.next_run_time = job.calculate_next_run_time()
            job.save()
            
            # Add the scheduled job
            scheduler.add_job(
                execute_job,
                CronTrigger.from_crontab(job.cron_expression),
                id=str(job.job_id),
                name=job.job_name,
                args=[job.job_id],
                replace_existing=True
            )
            
            logger.info(f"Added scheduled job: {job.job_name}")
        except Exception as e:
            logger.error(f"Failed to add scheduled job {job.job_name}: {str(e)}")
    
    scheduler.start()
    return scheduler 

