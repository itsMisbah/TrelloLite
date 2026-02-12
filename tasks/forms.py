from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    """Form for creating and updating tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'status', 'priority', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the task in detail...'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """Customize form based on workspace"""
        workspace = kwargs.pop('workspace', None)
        super().__init__(*args, **kwargs)
        
        # Only show workspace members in assigned_to dropdown
        if workspace:
            self.fields['assigned_to'].queryset = workspace.get_all_members()
            self.fields['assigned_to'].empty_label = "Unassigned"


class TaskFilterForm(forms.Form):
    """Form for filtering tasks"""
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Task.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + Task.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    assigned_to = forms.ChoiceField(
        choices=[('', 'All Assignees')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        workspace = kwargs.pop('workspace', None)
        super().__init__(*args, **kwargs)
        
        if workspace:
            members = workspace.get_all_members()
            choices = [('', 'All Assignees'), ('unassigned', 'Unassigned')]
            choices += [(m.id, m.username) for m in members]
            self.fields['assigned_to'].choices = choices