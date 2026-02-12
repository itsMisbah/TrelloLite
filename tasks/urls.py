from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Workspace tasks
    path('workspace/<int:workspace_id>/', views.TaskListView.as_view(), name='list'),
    path('workspace/<int:workspace_id>/create/', views.TaskCreateView.as_view(), name='create'),
    
    # Individual task
    path('<int:pk>/', views.TaskDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),
    path('<int:pk>/toggle-status/', views.toggle_task_status, name='toggle_status'),
]