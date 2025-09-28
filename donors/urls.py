from django.urls import path
from . import views

app_name = 'donors'
urlpatterns = [
    path('register/', views.donor_registration, name='donor_registration'),
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('donation-entry/', views.donation_entry, name='donation_entry'),  # Correct pattern
    path('login/', views.donor_login, name='donor_login'),
    path('logout/', views.donor_logout, name='donor_logout'),
]