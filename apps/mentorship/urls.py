from django.urls import path
from . import views

app_name = 'mentorship'

urlpatterns = [
    # Public URLs - Browse mentors
    path('', views.mentor_list, name='list'),
    path('<int:pk>/', views.mentor_detail, name='detail'),
    path('<int:mentor_id>/book/', views.book_session, name='book'),
]
