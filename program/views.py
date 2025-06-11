from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from .models import Program
from static.utils.db_utils import retry_on_db_lock
import json
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def program_view(request):
    return render(request, 'program/program.html')

@retry_on_db_lock
def create_program(request):
    """創建程式"""
    try:
        data = json.loads(request.body)
        with transaction.atomic():
            program = Program.objects.create(
                program_name=data['program_name'],
                workspace_id=data['workspace_id'],
                report_name=data['report_name'],
                dataset_id=data['dataset_id'],
                method=data['method'],
                output_name=data['output_name'],
                output_type=data['output_type'],
                sharepoint_site=data['sharepoint_site'],
                sharepoint_path=data['sharepoint_path'],
                filelocation=data['filelocation'],
                description=data.get('description', '')
            )
        return JsonResponse({'status': 'success', 'program_id': program.program_id})
    except Exception as e:
        logger.error(f"Error creating program: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@retry_on_db_lock
def update_program(request, program_id):
    """更新程式"""
    try:
        data = json.loads(request.body)
        with transaction.atomic():
            program = Program.objects.get(program_id=program_id)
            for field in ['program_name', 'workspace_id', 'report_name', 'dataset_id',
                         'method', 'output_name', 'output_type', 'sharepoint_site',
                         'sharepoint_path', 'filelocation', 'description']:
                if field in data:
                    setattr(program, field, data[field])
            program.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error updating program: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@retry_on_db_lock
def delete_program(request, program_id):
    """刪除程式"""
    try:
        with transaction.atomic():
            program = Program.objects.get(program_id=program_id)
            program.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error deleting program: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)