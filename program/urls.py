from django.urls import path
from . import views

urlpatterns = [
    path('', views.program_view, name='program'),
    path('create/', views.create_program_view, name='create_program'),
]
