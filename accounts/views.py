from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from .models import Group, User
from static.utils.db_utils import retry_on_db_lock
import json
import logging

logger = logging.getLogger(__name__)

def group_view(request):
    return render(request, 'accounts/group.html')

@retry_on_db_lock
def create_group(request):
    """創建群組"""
    try:
        data = json.loads(request.body)
        with transaction.atomic():
            group = Group.objects.create(
                group_name=data['group_name'],
                user_id=request.user,
                description=data.get('description', '')
            )
        return JsonResponse({'status': 'success', 'group_id': group.group_id})
    except Exception as e:
        logger.error(f"Error creating group: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@retry_on_db_lock
def update_group(request, group_id):
    """更新群組"""
    try:
        data = json.loads(request.body)
        with transaction.atomic():
            group = Group.objects.get(group_id=group_id)
            group.group_name = data.get('group_name', group.group_name)
            group.description = data.get('description', group.description)
            group.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error updating group: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@retry_on_db_lock
def delete_group(request, group_id):
    """刪除群組"""
    try:
        with transaction.atomic():
            group = Group.objects.get(group_id=group_id)
            group.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error deleting group: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def user_view(request):
    return render(request, 'accounts/user.html')

@retry_on_db_lock
def create_user(request):
    """創建使用者"""
    try:
        data = json.loads(request.body)
        with transaction.atomic():
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                description=data.get('description', '')
            )
        return JsonResponse({'status': 'success', 'user_id': user.user_id})
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@retry_on_db_lock
def update_user(request, user_id):
    """更新使用者"""
    try:
        data = json.loads(request.body)
        with transaction.atomic():
            user = User.objects.get(user_id=user_id)
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'description' in data:
                user.description = data['description']
            if 'password' in data:
                user.set_password(data['password'])
            user.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@retry_on_db_lock
def delete_user(request, user_id):
    """刪除使用者"""
    try:
        with transaction.atomic():
            user = User.objects.get(user_id=user_id)
            user.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
