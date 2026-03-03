from django.urls import path
from . import views

app_name = 'workspace'

urlpatterns = [
    path('', views.workspace_list, name='list'),
    path('create/', views.create_workspace, name='create'),
    path('<int:pk>/', views.workspace_detail, name='detail'),
    path('<int:pk>/project/create/', views.create_project, name='create_project'),
]
