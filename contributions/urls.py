# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('contribute/', views.contribute, name='contribute'),
    path('cycle/', views.manage_cycle, name='cycle'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('create_group/', views.dashboard, name='create_group'),  # Reuse dashboard logic
    path('join_group/', views.dashboard, name='join_group'),      # Reuse dashboard logic
]