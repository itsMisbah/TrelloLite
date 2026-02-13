from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from .models import Task, Comment
from .forms import TaskForm, TaskFilterForm, CommentForm
from workspaces.models import Workspace


class TaskListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """List all tasks in a workspace with filtering"""
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20
    
    def test_func(self):
        """Only workspace members can view tasks"""
        workspace = get_object_or_404(Workspace, pk=self.kwargs['workspace_id'])
        return workspace.is_owner(self.request.user) or workspace.is_member(self.request.user)
    
    def get_queryset(self):
        """Return filtered tasks for workspace"""
        workspace_id = self.kwargs['workspace_id']
        queryset = Task.objects.filter(workspace_id=workspace_id)
        
        # Apply filters
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        assigned_to = self.request.GET.get('assigned_to')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if priority:
            queryset = queryset.filter(priority=priority)
        
        if assigned_to:
            if assigned_to == 'unassigned':
                queryset = queryset.filter(assigned_to__isnull=True)
            else:
                queryset = queryset.filter(assigned_to_id=assigned_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace = get_object_or_404(Workspace, pk=self.kwargs['workspace_id'])
        context['workspace'] = workspace
        context['filter_form'] = TaskFilterForm(
            self.request.GET or None,
            workspace=workspace
        )
        
        # Task counts
        context['total_tasks'] = workspace.tasks.count()
        context['todo_count'] = workspace.tasks.filter(status=Task.STATUS_TODO).count()
        context['in_progress_count'] = workspace.tasks.filter(status=Task.STATUS_IN_PROGRESS).count()
        context['done_count'] = workspace.tasks.filter(status=Task.STATUS_DONE).count()
        
        return context


class TaskDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a single task"""
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    
    def test_func(self):
        """Only workspace members can view task"""
        task = self.get_object()
        user = self.request.user
        return task.workspace.is_owner(user) or task.workspace.is_member(user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        context['can_edit'] = task.can_edit(self.request.user)
        context['can_delete'] = task.can_delete(self.request.user)
        context['comment_form'] = CommentForm()
        comments = task.comments.all()  
        context['comments'] = comments  

        for comment in comments:
            comment.can_edit_by_user = comment.can_edit(self.request.user)
            comment.can_delete_by_user = comment.can_delete(self.request.user)

        return context


class TaskCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new task in workspace"""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def test_func(self):
        """Only workspace members can create tasks"""
        workspace = get_object_or_404(Workspace, pk=self.kwargs['workspace_id'])
        return workspace.is_owner(self.request.user) or workspace.is_member(self.request.user)
    
    def get_form_kwargs(self):
        """Pass workspace to form"""
        kwargs = super().get_form_kwargs()
        kwargs['workspace'] = get_object_or_404(Workspace, pk=self.kwargs['workspace_id'])
        return kwargs
    
    def form_valid(self, form):
        """Set workspace and created_by before saving"""
        form.instance.workspace = get_object_or_404(Workspace, pk=self.kwargs['workspace_id'])
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Task "{form.instance.title}" created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to workspace task list"""
        return reverse('tasks:list', kwargs={'workspace_id': self.kwargs['workspace_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workspace'] = get_object_or_404(Workspace, pk=self.kwargs['workspace_id'])
        return context


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing task"""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def test_func(self):
        """Only authorized users can update task"""
        task = self.get_object()
        return task.can_edit(self.request.user)
    
    def get_form_kwargs(self):
        """Pass workspace to form"""
        kwargs = super().get_form_kwargs()
        kwargs['workspace'] = self.get_object().workspace
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f'Task "{form.instance.title}" updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to task detail"""
        return reverse('tasks:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workspace'] = self.get_object().workspace
        return context


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a task"""
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    
    def test_func(self):
        """Only authorized users can delete task"""
        task = self.get_object()
        return task.can_delete(self.request.user)
    
    def get_success_url(self):
        """Redirect to workspace task list"""
        workspace_id = self.object.workspace.pk
        messages.success(self.request, f'Task "{self.object.title}" deleted successfully!')
        return reverse('tasks:list', kwargs={'workspace_id': workspace_id})


@login_required
def toggle_task_status(request, pk):
    """Quick toggle task status (TODO → IN_PROGRESS → DONE → TODO)"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check permission
    if not task.can_edit(request.user):
        messages.error(request, "You don't have permission to edit this task.")
        return redirect('tasks:detail', pk=pk)
    
    # Toggle status
    if task.status == Task.STATUS_TODO:
        task.status = Task.STATUS_IN_PROGRESS
    elif task.status == Task.STATUS_IN_PROGRESS:
        task.status = Task.STATUS_DONE
    else:  # DONE
        task.status = Task.STATUS_TODO
    
    task.save()
    messages.success(request, f'Task status updated to "{task.get_status_display()}"')
    
    # Redirect back to referring page or task detail
    return redirect(request.META.get('HTTP_REFERER', reverse('tasks:detail', kwargs={'pk': pk})))


@login_required
def add_comment(request, task_id):
    """Add a comment to a task"""
    task = get_object_or_404(Task, pk=task_id)
    
    # Check if user can access this task
    if not (task.workspace.is_owner(request.user) or task.workspace.is_member(request.user)):
        messages.error(request, "You don't have permission to comment on this task.")
        return redirect('tasks:detail', pk=task_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            messages.success(request, "Comment added successfully!")
        else:
            messages.error(request, "Error adding comment. Please try again.")
    
    return redirect('tasks:detail', pk=task_id)


@login_required
def edit_comment(request, pk):
    """Edit a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    
    # Check permission
    if not comment.can_edit(request.user):
        messages.error(request, "You can only edit your own comments.")
        return redirect('tasks:detail', pk=comment.task.pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated successfully!")
            return redirect('tasks:detail', pk=comment.task.pk)
    else:
        form = CommentForm(instance=comment)
    
    context = {
        'form': form,
        'comment': comment,
        'task': comment.task,
    }
    return render(request, 'tasks/comment_edit.html', context)


@login_required
def delete_comment(request, pk):
    """Delete a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    task_pk = comment.task.pk
    
    # Check permission
    if not comment.can_delete(request.user):
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('tasks:detail', pk=task_pk)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted successfully!")
        return redirect('tasks:detail', pk=task_pk)
    
    context = {
        'comment': comment,
        'task': comment.task,
    }
    return render(request, 'tasks/comment_confirm_delete.html', context)