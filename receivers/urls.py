from django.urls import path
from . import views

app_name = 'receivers'
urlpatterns = [
    path('register/', views.receiver_registration, name='receiver_registration'),
    path('dashboard/', views.receiver_dashboard, name='receiver_dashboard'),
    path('login/', views.receiver_login, name='receiver_login'),
    path('logout/', views.receiver_logout, name='receiver_logout'),
]

