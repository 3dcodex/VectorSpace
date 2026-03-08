from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Workspace, Project

@login_required
def workspace_list(request):
    workspaces = request.user.workspaces.all()
    return render(request, 'workspace/list.html', {'workspaces': workspaces})

@login_required
def create_workspace(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        workspace = Workspace.objects.create(
            owner=request.user,
            name=name,
            description=description
        )
        
        messages.success(request, 'Workspace created!')
        return redirect('workspace:detail', pk=workspace.pk)
    
    return render(request, 'workspace/create.html')

@login_required
def workspace_detail(request, pk):
    workspace = get_object_or_404(Workspace, pk=pk)
    
    # Check if user is member
    if not workspace.members.filter(pk=request.user.pk).exists():
        messages.error(request, 'You do not have access to this workspace.')
        return redirect('workspace:list')
    
    projects = workspace.projects.all()
    
    return render(request, 'workspace/detail.html', {
        'workspace': workspace,
        'projects': projects
    })

@login_required
def create_project(request, pk):
    workspace = get_object_or_404(Workspace, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        project = Project.objects.create(
            workspace=workspace,
            name=name,
            description=description
        )
        
        messages.success(request, 'Project created!')
        return redirect('workspace:detail', pk=pk)
    
    return render(request, 'workspace/create_project.html', {'workspace': workspace})
