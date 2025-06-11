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
from django.db import transaction
from threading import Lock
from django.core.cache import cache

logger = logging.getLogger(__name__)

# 創建一個鎖來控制資料庫訪問
db_lock = Lock()

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
        
        # 構建程式參數並轉換為 JSON
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
        
        # 等待進程完成或超時
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return False, "Execution timed out (over 1 hour)."
        
        return process.returncode == 0, stdout or stderr
            
    except Exception as e:
        logger.error(f"Error executing Power BI Engine: {str(e)}")
        return False, str(e)

def execute_job(job_id):
    """執行任務"""
    try:
        with db_lock:  # 使用鎖保護資料庫操作
            job = JobScheduler.objects.get(job_id=job_id)
            execution = JobExecution.objects.create(
                job=job,
                status='running'
            )
            job.last_run_time = timezone.now()
            job.next_run_time = job.calculate_next_run_time()
            job.save()
        
        # 執行任務
        result = execute_powerbi_engine(job.program, execution.execution_id)
        
        # 更新執行狀態
        with db_lock:
            execution.status = 'completed' if result[0] else 'failed'
            if not result[0]:
                execution.error = result[1]
            execution.end_time = timezone.now()
            execution.save()
        
    except Exception as e:
        logger.error(f"Error executing job {job_id}: {str(e)}")
        if execution:
            with db_lock:
                execution.status = 'failed'
                execution.error = str(e)
                execution.end_time = timezone.now()
                execution.save()

def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # 使用快取獲取啟用的任務
    cache_key = 'enabled_jobs'
    jobs = cache.get(cache_key)
    
    if not jobs:
        with db_lock:  # 使用鎖保護資料庫操作
            jobs = JobScheduler.objects.filter(enabled=True)
            cache.set(cache_key, list(jobs), 300)  # 快取 5 分鐘
    
    for job in jobs:
        try:
            with db_lock:  # 使用鎖保護資料庫操作
                job.next_run_time = job.calculate_next_run_time()
                job.save()
            
            scheduler.add_job(
                execute_job,
                CronTrigger.from_crontab(job.cron_expression),
                id=str(job.job_id),
                name=job.job_name,
                args=[job.job_id],
                replace_existing=True,
                max_instances=1
            )
            
            logger.info(f"Added scheduled job: {job.job_name}")
        except Exception as e:
            logger.error(f"Failed to add scheduled job {job.job_name}: {str(e)}")
    
    scheduler.start()
    return scheduler 

