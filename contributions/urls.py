# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('contribute/', views.contribute, name='contribute'),
    path('cycle/', views.manage_cycle, name='cycle'),
]