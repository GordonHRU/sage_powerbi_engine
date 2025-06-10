from django.urls import path
from . import views

urlpatterns = [
    path('email_template/', views.email_template_view, name='email_template'),      # 群組頁面
    path('job_properties/', views.job_properties_view, name='job_properties'),         # 使用者頁面
]