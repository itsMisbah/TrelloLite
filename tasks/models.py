from django.db import models
from django.conf import settings
from django.urls import reverse
from workspaces.models import Workspace
from django.utils import timezone


class Task(models.Model):
    """
    Task model - represents a task within a workspace.
    Tasks can be assigned to workspace members and have status/priority.
    """
    
    # Status choices
    STATUS_TODO = 'TODO'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_DONE = 'DONE'
    
    STATUS_CHOICES = [
        (STATUS_TODO, 'To Do'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_DONE, 'Done'),
    ]
    
    # Priority choices
    PRIORITY_LOW = 'LOW'
    PRIORITY_MEDIUM = 'MEDIUM'
    PRIORITY_HIGH = 'HIGH'
    
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Detailed description of the task")
    
    # Relationships
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="Workspace this task belongs to"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        help_text="User who created this task"
    )
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks',
        null=True,
        blank=True,
        help_text="User assigned to this task"
    )
    
    # Task properties
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_TODO
    )
    
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM
    )
    
    due_date = models.DateField(null=True, blank=True, help_text="When should this task be completed?")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Return URL for task detail page"""
        return reverse('tasks:detail', kwargs={'pk': self.pk})
    
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status != self.STATUS_DONE:
            return self.due_date < timezone.now().date()
        return False
    
    def get_status_badge_class(self):
        """Return Bootstrap badge class based on status"""
        return {
            self.STATUS_TODO: 'secondary',
            self.STATUS_IN_PROGRESS: 'primary',
            self.STATUS_DONE: 'success',
        }.get(self.status, 'secondary')
    
    def get_priority_badge_class(self):
        """Return Bootstrap badge class based on priority"""
        return {
            self.PRIORITY_LOW: 'info',
            self.PRIORITY_MEDIUM: 'warning',
            self.PRIORITY_HIGH: 'danger',
        }.get(self.priority, 'secondary')
    
    def can_edit(self, user):
        """Check if user can edit this task"""
        # Owner of workspace, creator, or assignee can edit
        return (
            self.workspace.is_owner(user) or
            self.created_by == user or
            self.assigned_to == user
        )
    
    def can_delete(self, user):
        """Check if user can delete this task"""
        # Only workspace owner or task creator can delete
        return self.workspace.is_owner(user) or self.created_by == user
    

class Comment(models.Model):
    """
    Comment model - represents a comment on a task.
    Users can comment on tasks they have access to.
    """
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Task this comment belongs to"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="User who wrote this comment"
    )
    
    text = models.TextField(help_text="Comment text")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']  # Oldest first
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
    
    def __str__(self):
        return f"{self.user.username} on {self.task.title}"
    
    def can_edit(self, user):
        """Check if user can edit this comment"""
        return self.user == user
    
    def can_delete(self, user):
        """Check if user can delete this comment"""
        # User can delete own comment OR workspace owner can delete any comment
        return self.user == user or self.task.workspace.is_owner(user)
    
    def is_edited(self):
        """Check if comment was edited"""
        return self.updated_at > self.created_at + timezone.timedelta(seconds=1)