from django.shortcuts import render

# Create your views here.
def job_scheduler_view(request):
    
    return render(request, 'job_scheduler/job_scheduler.html')

def create_job_view(request):
    return render(request, 'job_scheduler/create_job.html')
