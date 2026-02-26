from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from tasks.models import Task, Comment
from workspaces.models import Workspace
from api.serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskListSerializer,
    CommentSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task CRUD"""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    def get_queryset(self):
        """Return tasks from user's workspaces"""
        user = self.request.user
        
        # Get workspaces where user is owner or member
        workspaces = Workspace.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()
        
        # Filter tasks by workspace_id if provided
        queryset = Task.objects.filter(workspace__in=workspaces)
        
        # Filter by workspace if specified
        workspace_id = self.request.query_params.get('workspace')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filter by assigned user
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            if assigned_to == 'me':
                queryset = queryset.filter(assigned_to=user)
            elif assigned_to == 'unassigned':
                queryset = queryset.filter(assigned_to__isnull=True)
            else:
                queryset = queryset.filter(assigned_to_id=assigned_to)
        
        return queryset.select_related('workspace', 'created_by', 'assigned_to').prefetch_related('comments')
    
    def perform_create(self, serializer):
        """Set workspace and created_by"""
        workspace_id = self.request.data.get('workspace_id')
        workspace = Workspace.objects.get(id=workspace_id)
        
        # Check if user is member of workspace
        if not (workspace.is_owner(self.request.user) or workspace.is_member(self.request.user)):
            raise PermissionError("You are not a member of this workspace")
        
        serializer.save(
            workspace=workspace,
            created_by=self.request.user
        )
    
    def update(self, request, *args, **kwargs):
        """Only authorized users can update task"""
        task = self.get_object()
        if not task.can_edit(request.user):
            return Response(
                {'error': 'You do not have permission to edit this task'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Only authorized users can delete task"""
        task = self.get_object()
        if not task.can_delete(request.user):
            return Response(
                {'error': 'You do not have permission to delete this task'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle task status (TODO → IN_PROGRESS → DONE → TODO)"""
        task = self.get_object()
        
        if not task.can_edit(request.user):
            return Response(
                {'error': 'You do not have permission to edit this task'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if task.status == Task.STATUS_TODO:
            task.status = Task.STATUS_IN_PROGRESS
        elif task.status == Task.STATUS_IN_PROGRESS:
            task.status = Task.STATUS_DONE
        else:
            task.status = Task.STATUS_TODO
        
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get all comments for a task"""
        task = self.get_object()
        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add comment to task"""
        task = self.get_object()
        
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(task=task, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment CRUD"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        """Return comments from user's accessible tasks"""
        user = self.request.user
        
        # Get workspaces where user is owner or member
        workspaces = Workspace.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()
        
        return Comment.objects.filter(task__workspace__in=workspaces).select_related('user', 'task')
    
    def update(self, request, *args, **kwargs):
        """Only comment author can update"""
        comment = self.get_object()
        if not comment.can_edit(request.user):
            return Response(
                {'error': 'You can only edit your own comments'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Author or workspace owner can delete"""
        comment = self.get_object()
        if not comment.can_delete(request.user):
            return Response(
                {'error': 'You do not have permission to delete this comment'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)