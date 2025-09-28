from django.urls import path
from . import views

app_name = 'receivers'

urlpatterns = [
    path('', views.receiver_login, name='receiver_login'),
    path('register/', views.receiver_registration, name='receiver_registration'),  # Verify this line
    path('dashboard/', views.receiver_dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('check_notification/<int:receiver_id>/', views.check_notification, name='check_notification'),
    path('schedule_pickup/<int:donation_id>/', views.schedule_pickup, name='schedule_pickup'),
]