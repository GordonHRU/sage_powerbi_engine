from django.shortcuts import render

# Create your views here.

def group_view(request):
    return render(request, 'accounts/group.html')

def user_view(request):
    return render(request, 'accounts/user.html')
