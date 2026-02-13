from django.contrib import admin
from .models import Task, Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task"""
    
    list_display = ['title', 'workspace', 'assigned_to', 'status', 'priority', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'workspace', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'workspace__name']
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'workspace')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-set created_by if creating new task"""
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# Add Comment Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment"""
    
    list_display = ['user', 'task', 'text_preview', 'created_at']
    list_filter = ['created_at', 'task__workspace']
    search_fields = ['text', 'user__username', 'task__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def text_preview(self, obj):
        """Show preview of comment text"""
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Comment"