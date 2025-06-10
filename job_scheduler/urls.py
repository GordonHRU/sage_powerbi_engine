from django.urls import path
from . import views

urlpatterns = [
    path('job_scheduler/', views.job_scheduler_view, name='job_scheduler'),
    path('job_scheduler/create_job/', views.create_job_view, name='create_job'),
] 
