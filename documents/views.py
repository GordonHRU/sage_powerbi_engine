from django.shortcuts import render

# Create your views here.
def email_template_view(request):
    return render(request, 'documents/email_template.html')

def job_properties_view(request):
    return render(request, 'documents/job_properties.html')

