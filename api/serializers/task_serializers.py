from rest_framework import serializers
from tasks.models import Task, Comment
from .user_serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    
    user = UserSerializer(read_only=True)
    is_edited = serializers.BooleanField(read_only=True)
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'task', 'user', 'text',
            'is_edited', 'can_edit', 'can_delete',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.can_edit(request.user)
        return False
    
    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.can_delete(request.user)
        return False


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'workspace', 'workspace_name',
            'created_by', 'assigned_to', 'assigned_to_id',
            'status', 'status_display', 'priority', 'priority_display',
            'due_date', 'is_overdue', 'can_edit', 'can_delete',
            'comments', 'comment_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'workspace', 'created_at', 'updated_at']
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.can_edit(request.user)
        return False
    
    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.can_delete(request.user)
        return False
    
    def get_comment_count(self, obj):
        return obj.comments.count()


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks"""
    
    assigned_to_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assigned_to_id',
            'status', 'priority', 'due_date'
        ]
    
    def validate_assigned_to_id(self, value):
        if value:
            from accounts.models import User
            try:
                User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("User not found")
        return value


class TaskListSerializer(serializers.ModelSerializer):
    """Simplified serializer for task lists"""
    
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'workspace', 'workspace_name',
            'assigned_to', 'created_by',
            'status', 'status_display', 'priority', 'priority_display',
            'due_date', 'is_overdue', 'created_at', 'updated_at'
        ]