# TaskFlow - Team Task Management System

A modern, feature-rich task management application built with Django. TaskFlow helps teams organize projects, assign tasks, track progress, and collaborate efficiently.

## Features

### Core Features
- **User Authentication** - Secure signup/login with email verification
- **Workspaces** - Create team workspaces for different projects
- **Tasks** - Full CRUD operations with status tracking
- **Team Collaboration** - Invite members and assign tasks
- **Comments** - Discuss tasks with team members
- **Dashboard** - Overview of all tasks and workspaces
- **Search** - Quick search across workspaces and tasks
- **User Profiles** - Customizable profiles with avatars

### Permissions & Security
- Workspace owners have full control
- Members can create and edit assigned tasks
- Comment editing restricted to authors
- Workspace-level access control

## Tech Stack

- **Backend**: Django 5.x
- **Database**: PostgreSQL
- **Authentication**: django-allauth
- **Frontend**: Bootstrap 5, HTML5, CSS3

## Installation

### Prerequisites
- Python 3.10+
- pip
- virtualenv (recommended)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/taskflow.git
cd taskflow
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

## 📸 Screenshots

### Dashboard
[Dashboard](screenshots/dashboard.png)

### Workspace Detail
![Workspace](screenshots/workspace.png)

### Profile Detail
![Workspace](screenshots/profile.png)

## Project Structure
```
taskflow/
├── accounts/          # User management
├── core/             # Dashboard & search
├── workspaces/       # Workspace management
├── tasks/            # Task management
├── templates/        # HTML templates
├── static/           # CSS, JS, images
├── media/            # User uploads
└── config/           # Project settings
```

## License

This project is licensed under the MIT License.

## Author

**Misbah Sultan**
- LinkedIn: [Misbah-Shahzadi](www.linkedin.com/in/misbah-shahzadi)
- Email: misbahh77777@gmail.com.com

