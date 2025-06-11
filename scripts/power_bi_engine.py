#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import sys
import os
from datetime import datetime
import time

# Set up logging
def setup_logging(execution_id):
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'power_bi_engine_{execution_id}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Power BI Engine')
    parser.add_argument('--program', type=str, required=True, help='Program parameters in JSON format')
    return parser.parse_args()

def main():
    try:
        # Parse arguments
        args = parse_args()
        program_params = json.loads(args.program)
        
        # Set up logging
        execution_id = program_params.get('execution_id', 'unknown')
        logger = setup_logging(execution_id)
        
        logger.info(f"Start Power BI Engine, execution ID: {execution_id}")
        logger.info(f"Job parameters: {json.dumps(program_params, ensure_ascii=False)}")
        
        # TODO: Implement Power BI Engine logic here
        # For example:
        # 1. Connect to Power BI service
        # 2. Execute data refresh
        # 3. Process output files

        # Simulate work with status updates every 5 seconds
        total_steps = 12  # 1 minute total with 5-second intervals
        for step in range(total_steps):
            progress = (step + 1) / total_steps * 100
            status_message = f"Processing... {progress:.1f}% complete"
            logger.info(status_message)
            time.sleep(5)  # 5 seconds interval
        
        # Log completion
        success_message = f"Power BI Engine completed successfully, ID: {execution_id}"
        logger.info(success_message)
        
    except Exception as e:
        error_message = f"Error occurred during execution: {str(e)}"
        logger.error(error_message)
        sys.exit(1)

if __name__ == '__main__':
    main() 