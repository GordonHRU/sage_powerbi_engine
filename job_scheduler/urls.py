from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_scheduler_view, name='job_scheduler'),
    path('create_job/', views.create_job_view, name='create_job'),
] 
