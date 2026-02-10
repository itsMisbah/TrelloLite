from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Workspace
from accounts.models import User


class WorkspaceListView(LoginRequiredMixin, ListView):
    """List all workspaces where user is owner or member"""
    model = Workspace
    template_name = 'workspaces/workspace_list.html'
    context_object_name = 'workspaces'
    
    def get_queryset(self):
        """Return workspaces where user is owner or member"""
        user = self.request.user
        return Workspace.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()


class WorkspaceDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a single workspace"""
    model = Workspace
    template_name = 'workspaces/workspace_detail.html'
    context_object_name = 'workspace'
    
    def test_func(self):
        """Only owner or members can view workspace"""
        workspace = self.get_object()
        user = self.request.user
        return workspace.is_owner(user) or workspace.is_member(user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace = self.get_object()
        context['is_owner'] = workspace.is_owner(self.request.user)
        context['all_members'] = workspace.get_all_members()
        return context


class WorkspaceCreateView(LoginRequiredMixin, CreateView):
    """Create a new workspace"""
    model = Workspace
    template_name = 'workspaces/workspace_form.html'
    fields = ['name', 'description']
    
    def form_valid(self, form):
        """Set the owner to current user"""
        form.instance.owner = self.request.user
        messages.success(self.request, f'Workspace "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class WorkspaceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update workspace (only owner can update)"""
    model = Workspace
    template_name = 'workspaces/workspace_form.html'
    fields = ['name', 'description']
    
    def test_func(self):
        """Only owner can update workspace"""
        workspace = self.get_object()
        return workspace.is_owner(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, f'Workspace "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class WorkspaceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete workspace (only owner can delete)"""
    model = Workspace
    template_name = 'workspaces/workspace_confirm_delete.html'
    success_url = reverse_lazy('workspaces:list')
    
    def test_func(self):
        """Only owner can delete workspace"""
        workspace = self.get_object()
        return workspace.is_owner(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        workspace = self.get_object()
        messages.success(request, f'Workspace "{workspace.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
def add_member(request, pk):
    """Add member to workspace (only owner can add)"""
    workspace = get_object_or_404(Workspace, pk=pk)
    
    # Check if user is owner
    if not workspace.is_owner(request.user):
        messages.error(request, "Only workspace owner can add members.")
        return redirect('workspaces:detail', pk=pk)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            
            # Check if already member
            if workspace.is_member(user):
                messages.warning(request, f"{user.username} is already a member.")
            elif workspace.owner == user:
                messages.warning(request, "Owner is automatically a member.")
            else:
                workspace.add_member(user)
                messages.success(request, f"{user.username} added to workspace!")
        except User.DoesNotExist:
            messages.error(request, f"User '{username}' not found.")
    
    return redirect('workspaces:detail', pk=pk)


@login_required
def remove_member(request, pk, user_id):
    """Remove member from workspace (only owner can remove)"""
    workspace = get_object_or_404(Workspace, pk=pk)
    user_to_remove = get_object_or_404(User, pk=user_id)
    
    # Check if user is owner
    if not workspace.is_owner(request.user):
        messages.error(request, "Only workspace owner can remove members.")
        return redirect('workspaces:detail', pk=pk)
    
    # Can't remove owner
    if user_to_remove == workspace.owner:
        messages.error(request, "Cannot remove workspace owner.")
        return redirect('workspaces:detail', pk=pk)
    
    workspace.remove_member(user_to_remove)
    messages.success(request, f"{user_to_remove.username} removed from workspace.")
    
    return redirect('workspaces:detail', pk=pk)