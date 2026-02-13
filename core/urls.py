from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
]