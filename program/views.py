from django.shortcuts import render

# Create your views here.
def program_view(request):
    return render(request, 'program/program.html')