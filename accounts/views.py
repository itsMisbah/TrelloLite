from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserProfileForm
from .models import User


@login_required
def profile(request):
    """View user profile"""
    user = request.user
    
    # Get user statistics
    from workspaces.models import Workspace
    from tasks.models import Task
    from django.db.models import Q
    
    owned_workspaces = Workspace.objects.filter(owner=user).count()
    member_workspaces = Workspace.objects.filter(members=user).count()
    
    created_tasks = Task.objects.filter(created_by=user).count()
    assigned_tasks = Task.objects.filter(assigned_to=user).count()
    completed_tasks = Task.objects.filter(
        Q(created_by=user) | Q(assigned_to=user),
        status=Task.STATUS_DONE
    ).distinct().count()
    
    context = {
        'profile_user': user,
        'owned_workspaces': owned_workspaces,
        'member_workspaces': member_workspaces,
        'created_tasks': created_tasks,
        'assigned_tasks': assigned_tasks,
        'completed_tasks': completed_tasks,
    }
    
    return render(request, 'account/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'account/edit_profile.html', {'form': form})