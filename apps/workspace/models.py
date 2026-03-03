from django.db import models
from apps.users.models import User

class Workspace(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')
    name = models.CharField(max_length=200)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name='workspaces', through='WorkspaceMember')
    created_at = models.DateTimeField(auto_now_add=True)

class WorkspaceMember(models.Model):
    ROLES = [('owner', 'Owner'), ('admin', 'Admin'), ('member', 'Member')]
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)
    joined_at = models.DateTimeField(auto_now_add=True)

class Project(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Task(models.Model):
    STATUS = [('todo', 'To Do'), ('in_progress', 'In Progress'), ('review', 'Review'), ('done', 'Done')]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    status = models.CharField(max_length=20, choices=STATUS, default='todo')
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class File(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='workspace_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
