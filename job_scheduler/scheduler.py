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
from apscheduler.events import EVENT_JOB_ERROR
from static.utils.db_utils import retry_on_db_lock
import time
from django.db.utils import OperationalError

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

def execute_powerbi_engine(program):
    """
    執行 Power BI Engine 腳本
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
            'filelocation': program.filelocation
        }
        
        # 構建命令
        script_path = os.path.join('scripts', 'power_bi_engine.py')
        command = [
            'python',
            script_path,
            '--program', json.dumps(program_params, ensure_ascii=False)
        ]
        
        # 執行命令並設置超時
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return stdout, stderr if process.returncode != 0 else None
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return None, "執行超時 超過1小時 "
            
    except Exception as e:
        logger.error(f"執行 Power BI Engine 時發生錯誤: {str(e)}")
        return None, str(e)

def execute_job(job_id):
    """執行排程任務"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            # 從資料庫獲取任務資訊
            job = JobScheduler.objects.get(job_id=job_id)
            program = job.program
            
            # 創建執行記錄
            execution = JobExecution.objects.create(
                job=job,
                status='running',
                start_time=timezone.now()
            )
            
            try:
                # 執行 PowerBI 引擎
                output, error = execute_powerbi_engine(program)
                
                # 更新執行記錄
                execution.status = 'completed' if not error else 'failed'
                execution.end_time = timezone.now()
                execution.output = output
                execution.error = error
                execution.save()
                
                logger.info(f"任務 {job.job_name} 執行成功")
                break  # 成功執行，跳出重試循環
                
            except Exception as e:
                # 更新執行記錄為失敗
                execution.status = 'failed'
                execution.end_time = timezone.now()
                execution.error = str(e)
                execution.save()
                
                logger.error(f"任務 {job.job_name} 執行失敗: {str(e)}")
                break  # 執行失敗，跳出重試循環
                
        except OperationalError as e:
            if "database is locked" in str(e).lower():
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"資料庫鎖定，{wait_time} 秒後重試... (嘗試 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"資料庫鎖定，已重試 {max_retries} 次")
                    raise
            else:
                raise
        except Exception as e:
            logger.error(f"執行任務 {job_id} 時發生錯誤: {str(e)}")
            break  # 其他錯誤，跳出重試循環

@retry_on_db_lock
def init_scheduler():
    """初始化排程器"""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # 載入所有啟用的任務
    jobs = JobScheduler.objects.filter(enabled=True)
    for job in jobs:
        try:
            scheduler.add_job(
                execute_job,
                CronTrigger.from_crontab(job.cron_expression),
                id=str(job.job_id),
                name=job.job_name,
                args=[job.job_id],
                replace_existing=True,
                max_instances=1  # 限制同時執行的實例數
            )
            logger.info(f"已添加排程任務: {job.job_name}")
        except Exception as e:
            logger.error(f"添加排程任務 {job.job_name} 失敗: {str(e)}")
    
    # 設置 APScheduler 的錯誤處理
    scheduler.add_listener(
        lambda event: logger.error(f"排程器錯誤: {event.exception}") if event.exception else None,
        EVENT_JOB_ERROR
    )
    
    scheduler.start()
    return scheduler 

