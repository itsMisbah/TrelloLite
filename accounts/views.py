from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserProfileForm
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_mail_page(request):
    context = {}

    if request.method == 'POST':
        address = request.POST.get('address')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if address and subject:
            try:
                # example verification link
                verification_link = "https://yourapp.onrender.com/verify/test"

                # render HTML template
                html_content = render_to_string("verification_email.html", {
                    "user_name": "User",
                    "verification_link": verification_link
                })

                # create email
                email = EmailMultiAlternatives(
                    subject,
                    message,  # fallback text
                    settings.EMAIL_HOST_USER,
                    [address]
                )

                email.attach_alternative(html_content, "text/html")
                email.send()

                context['result'] = 'Email sent successfully'

            except Exception as e:
                context['result'] = f'Error sending email: {e}'
        else:
            context['result'] = 'All fields are required'

    return render(request, "verification_email.html", context)


@login_required
def profile(request):
    """View user profile"""
    user = request.user
    
    # Get user statistics
    from workspaces.models import Workspace
    from tasks.models import Task
    from django.db.models import Q
    
    owned_workspaces = Workspace.objects.filter(owner=user).count()
    member_workspaces = Workspace.objects.filter(members=user).count()
    
    created_tasks = Task.objects.filter(created_by=user).count()
    assigned_tasks = Task.objects.filter(assigned_to=user).count()
    completed_tasks = Task.objects.filter(
        Q(created_by=user) | Q(assigned_to=user),
        status=Task.STATUS_DONE
    ).distinct().count()
    
    context = {
        'profile_user': user,
        'owned_workspaces': owned_workspaces,
        'member_workspaces': member_workspaces,
        'created_tasks': created_tasks,
        'assigned_tasks': assigned_tasks,
        'completed_tasks': completed_tasks,
    }
    
    return render(request, 'account/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'account/edit_profile.html', {'form': form})