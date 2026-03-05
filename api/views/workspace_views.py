from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from workspaces.models import Workspace
from accounts.models import User
from api.serializers import (
    WorkspaceSerializer,
    WorkspaceCreateSerializer,
    WorkspaceMemberSerializer
)


class WorkspaceViewSet(viewsets.ModelViewSet):
    """ViewSet for Workspace CRUD"""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WorkspaceCreateSerializer
        return WorkspaceSerializer
    
    def get_queryset(self):
        """Return workspaces where user is owner or member"""
        user = self.request.user
        return Workspace.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct().select_related('owner').prefetch_related('members')
    
    def perform_create(self, serializer):
        """Set owner to current user"""
        serializer.save(owner=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Only owner can update workspace"""
        workspace = self.get_object()
        if not workspace.is_owner(request.user):
            return Response(
                {'error': 'Only workspace owner can update'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Only owner can delete workspace"""
        workspace = self.get_object()
        if not workspace.is_owner(request.user):
            return Response(
                {'error': 'Only workspace owner can delete'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to workspace"""
        workspace = self.get_object()
        
        if not workspace.is_owner(request.user):
            return Response(
                {'error': 'Only workspace owner can add members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = WorkspaceMemberSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            user = User.objects.get(username=username)
            
            if workspace.is_member(user):
                return Response(
                    {'error': 'User is already a member'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if workspace.owner == user:
                return Response(
                    {'error': 'Owner is automatically a member'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            workspace.add_member(user)
            return Response(
                {'message': f'{username} added to workspace'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove member from workspace"""
        workspace = self.get_object()
        
        if not workspace.is_owner(request.user):
            return Response(
                {'error': 'Only workspace owner can remove members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = WorkspaceMemberSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            user = User.objects.get(username=username)
            
            if user == workspace.owner:
                return Response(
                    {'error': 'Cannot remove workspace owner'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            workspace.remove_member(user)
            return Response(
                {'message': f'{username} removed from workspace'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)