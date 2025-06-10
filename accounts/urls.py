from django.urls import path
from . import views

urlpatterns = [
    path('group/', views.group_view, name='group'),      # 群組頁面
    path('user/', views.user_view, name='user'),         # 使用者頁面
]
