from django.db import models
from django.conf import settings
from django.urls import reverse


class Workspace(models.Model):
    """
    Workspace model - represents a team/project workspace.
    Each workspace has an owner and can have multiple members.
    """
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="What is this workspace about?")
    
    # Relationships
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_workspaces',
        help_text="User who created this workspace"
    )
    
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='workspaces',
        blank=True,
        help_text="Users who are members of this workspace"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Workspace'
        verbose_name_plural = 'Workspaces'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """Return URL for workspace detail page"""
        return reverse('workspaces:detail', kwargs={'pk': self.pk})
    
    def is_member(self, user):
        """Check if user is a member of this workspace"""
        return self.members.filter(pk=user.pk).exists()
    
    def is_owner(self, user):
        """Check if user is the owner of this workspace"""
        return self.owner == user
    
    def add_member(self, user):
        """Add a user as member"""
        if not self.is_member(user):
            self.members.add(user)
    
    def remove_member(self, user):
        """Remove a user from members"""
        if self.is_member(user):
            self.members.remove(user)
    
    def get_all_members(self):
        return self.members.all() 

    
    def member_count(self):
        return self.members.count()  