from django.shortcuts import render
from django.urls import reverse

# Create your views here.

def index(request):
    # context = {
    #     'programs_url': reverse('programs'),
    #     'job_scheduler_url': reverse('job_scheduler'),
    #     'accounts_url': reverse('accounts'),
        
    #     'documents_url': reverse('documents'),
    # }
    return render(request, 'core/index.html')

def configuration_view(request):
    return render(request, 'core/view.html')

