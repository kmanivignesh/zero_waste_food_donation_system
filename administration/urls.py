from django.urls import path
from . import views

app_name = 'administration'
urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('pickup-management/', views.pickup_management, name='pickup_management'),
    path('analytics/', views.analytics, name='analytics'),
]