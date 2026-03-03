from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify/<uuid:token>/', views.verify_email, name='verify_email'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/creator/', views.creator_dashboard, name='creator_dashboard'),
    path('dashboard/mentor/', views.mentor_dashboard, name='mentor_dashboard'),
    path('dashboard/recruiter/', views.recruiter_dashboard, name='recruiter_dashboard'),
]
