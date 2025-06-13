from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_scheduler_view, name='job_scheduler'),
    path('create/', views.create_job, name='create_job'),
    path('delete/<int:job_id>/', views.delete_job, name='delete_job'),
    path('api/job/<int:job_id>/status/', views.get_job_status, name='get_job_status'),
    path('api/job/<int:job_id>/history/', views.get_execution_history, name='get_execution_history'),
] 
