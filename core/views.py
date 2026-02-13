from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from workspaces.models import Workspace
from tasks.models import Task
from django.utils import timezone


@login_required
def dashboard(request):
    """Main dashboard view"""
    user = request.user
    
    # Get user's workspaces
    workspaces = Workspace.objects.filter(
        Q(owner=user) | Q(members=user)
    ).distinct()[:5]  # Latest 5

    for workspace in workspaces:
        workspace.is_owner_by_user = workspace.is_owner(user)
    
    # Get user's tasks (assigned or created)
    my_tasks = Task.objects.filter(
        Q(assigned_to=user) | Q(created_by=user)
    ).distinct().select_related('workspace', 'assigned_to')[:10]
    
    # Task statistics
    total_tasks = Task.objects.filter(
        Q(assigned_to=user) | Q(created_by=user)
    ).distinct().count()
    
    todo_tasks = Task.objects.filter(
        Q(assigned_to=user) | Q(created_by=user),
        status=Task.STATUS_TODO
    ).distinct().count()
    
    in_progress_tasks = Task.objects.filter(
        Q(assigned_to=user) | Q(created_by=user),
        status=Task.STATUS_IN_PROGRESS
    ).distinct().count()
    
    done_tasks = Task.objects.filter(
        Q(assigned_to=user) | Q(created_by=user),
        status=Task.STATUS_DONE
    ).distinct().count()
    
    # Overdue tasks
    overdue_tasks = Task.objects.filter(
        Q(assigned_to=user) | Q(created_by=user),
        due_date__lt=timezone.now().date(),
        status__in=[Task.STATUS_TODO, Task.STATUS_IN_PROGRESS]
    ).distinct()
    
    context = {
        'workspaces': workspaces,
        'my_tasks': my_tasks,
        'total_tasks': total_tasks,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
        'overdue_tasks': overdue_tasks,
        'total_workspaces': workspaces.count(),
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def my_tasks(request):
    """View all tasks assigned to or created by user"""
    user = request.user
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    # Base queryset
    tasks = Task.objects.filter(
        Q(assigned_to=user) | Q(created_by=user)
    ).distinct().select_related('workspace', 'assigned_to', 'created_by')
    
    # Apply filters
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    # Statistics
    total_count = tasks.count()
    todo_count = tasks.filter(status=Task.STATUS_TODO).count()
    in_progress_count = tasks.filter(status=Task.STATUS_IN_PROGRESS).count()
    done_count = tasks.filter(status=Task.STATUS_DONE).count()
    
    context = {
        'tasks': tasks,
        'total_count': total_count,
        'todo_count': todo_count,
        'in_progress_count': in_progress_count,
        'done_count': done_count,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'STATUS_CHOICES': Task.STATUS_CHOICES,
        'PRIORITY_CHOICES': Task.PRIORITY_CHOICES,
    }
    
    return render(request, 'core/my_tasks.html', context)