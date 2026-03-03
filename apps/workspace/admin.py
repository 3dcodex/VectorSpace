from django.contrib import admin
from .models import Workspace, WorkspaceMember, Project, Task, File

admin.site.register(Workspace)
admin.site.register(WorkspaceMember)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(File)
