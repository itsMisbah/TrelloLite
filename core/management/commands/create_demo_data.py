from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from workspaces.models import Workspace
from tasks.models import Task, Comment
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo data for TaskFlow'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating demo data...')

        # Create demo users
        demo_users = []
        usernames = ['alice', 'bob', 'charlie', 'diana']
        
        for username in usernames:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@demo.com',
                    'first_name': username.capitalize(),
                    'last_name': 'Demo',
                    'bio': f'Demo user {username}',
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
                self.stdout.write(f'Created user: {username}')
            demo_users.append(user)

        # Create demo workspaces
        workspaces_data = [
            {
                'name': 'Website Redesign',
                'description': 'Complete redesign of company website with modern UI/UX'
            },
            {
                'name': 'Mobile App Development',
                'description': 'Build iOS and Android mobile application'
            },
            {
                'name': 'Marketing Campaign Q1',
                'description': 'Plan and execute Q1 marketing campaigns'
            },
        ]

        workspaces = []
        for ws_data in workspaces_data:
            owner = random.choice(demo_users)
            workspace, created = Workspace.objects.get_or_create(
                name=ws_data['name'],
                defaults={
                    'description': ws_data['description'],
                    'owner': owner,
                }
            )
            if created:
                # Add random members
                members = random.sample([u for u in demo_users if u != owner], k=random.randint(1, 3))
                workspace.members.set(members)
                self.stdout.write(f'Created workspace: {workspace.name}')
            workspaces.append(workspace)

        # Create demo tasks
        tasks_data = [
            ('Design homepage mockup', 'Create initial mockup for homepage with new branding', Task.PRIORITY_HIGH),
            ('Setup development environment', 'Configure dev environment for all team members', Task.PRIORITY_MEDIUM),
            ('Write API documentation', 'Document all API endpoints with examples', Task.PRIORITY_MEDIUM),
            ('Fix mobile responsive issues', 'Resolve CSS issues on mobile devices', Task.PRIORITY_HIGH),
            ('Create user testing plan', 'Plan user testing sessions for new features', Task.PRIORITY_LOW),
            ('Update database schema', 'Add new fields to support new features', Task.PRIORITY_HIGH),
            ('Write unit tests', 'Add test coverage for new modules', Task.PRIORITY_MEDIUM),
            ('Deploy to staging', 'Deploy latest changes to staging environment', Task.PRIORITY_HIGH),
        ]

        statuses = [Task.STATUS_TODO, Task.STATUS_IN_PROGRESS, Task.STATUS_DONE]
        
        for i, (title, desc, priority) in enumerate(tasks_data):
            workspace = random.choice(workspaces)
            creator = workspace.owner
            assignee = random.choice(list(workspace.members.all()) + [workspace.owner])
            
            # Random due date
            days_offset = random.randint(-3, 7)
            due_date = timezone.now().date() + timedelta(days=days_offset)
            
            task, created = Task.objects.get_or_create(
                title=title,
                workspace=workspace,
                defaults={
                    'description': desc,
                    'created_by': creator,
                    'assigned_to': assignee,
                    'status': random.choice(statuses),
                    'priority': priority,
                    'due_date': due_date,
                }
            )
            
            if created:
                # Add random comments
                if random.random() > 0.5:  # 50% chance
                    comment_texts = [
                        'Great progress on this!',
                        'I have some questions about the requirements.',
                        'Updated the design based on feedback.',
                        'This is ready for review.',
                        'Added some improvements.',
                    ]
                    
                    num_comments = random.randint(1, 3)
                    for _ in range(num_comments):
                        commenter = random.choice(list(workspace.members.all()) + [workspace.owner])
                        Comment.objects.create(
                            task=task,
                            user=commenter,
                            text=random.choice(comment_texts),
                        )
                
                self.stdout.write(f'Created task: {title}')

        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))
        self.stdout.write('\nDemo users created:')
        for username in usernames:
            self.stdout.write(f'  Username: {username}, Password: demo123')