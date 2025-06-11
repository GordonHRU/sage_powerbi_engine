from django.db.utils import OperationalError
from django.db import connection
import time
import logging

logger = logging.getLogger(__name__)

def retry_on_db_lock(func):
    """資料庫操作重試裝飾器"""
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1  # 初始延遲1秒
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if "database is locked" in str(e).lower():
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # 指數退避
                        logger.warning(f"Database locked, retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        # 重置資料庫連接
                        connection.close()
                    else:
                        logger.error(f"Database locked after {max_retries} attempts")
                        raise
                else:
                    raise
    return wrapper 