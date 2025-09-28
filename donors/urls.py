from django.urls import path
from . import views

urlpatterns = [
    path('', views.donor_login, name='donor_login'),
    path('register/', views.donor_registration, name='donor_registration'),
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('donation-entry/', views.donation_entry, name='donation_entry'),
    path('logout/', views.donor_logout, name='donor_logout'),
    path('check_requests/<int:donor_id>/', views.check_requests, name='check_requests'),
]