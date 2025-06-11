from django.urls import path
from . import views

urlpatterns = [
    path('job_scheduler/', views.job_scheduler_view, name='job_scheduler'),
    path('job_scheduler/create_job/', views.create_job_view, name='create_job'),
    path('create/', views.create_job_view, name='create_job'),
    path('api/job/<int:job_id>/status/', views.get_job_status, name='get_job_status'),
    path('api/job/<int:job_id>/history/', views.get_execution_history, name='get_execution_history'),
] 
