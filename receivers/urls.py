from django.urls import path
from . import views

urlpatterns = [
    path('', views.receiver_login, name='receiver_login'),
    path('register/', views.receiver_registration, name='receiver_registration'),
    path('dashboard/', views.receiver_dashboard, name='receiver_dashboard'),
    path('logout/', views.receiver_logout, name='receiver_logout'),
    path('check_notification/<int:receiver_id>/', views.check_notification, name='check_notification'),
]