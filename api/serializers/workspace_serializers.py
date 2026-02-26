from rest_framework import serializers
from workspaces.models import Workspace
from .user_serializers import UserSerializer


class WorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for Workspace model"""
    
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    task_count = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    
    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'description', 'owner', 'members',
            'member_count', 'task_count', 'is_owner',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.is_owner(request.user)
        return False


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating workspace"""
    
    class Meta:
        model = Workspace
        fields = ['name', 'description']


class WorkspaceMemberSerializer(serializers.Serializer):
    """Serializer for adding/removing members"""
    
    username = serializers.CharField()
    
    def validate_username(self, value):
        from accounts.models import User
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value