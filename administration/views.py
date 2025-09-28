from django.shortcuts import render
from core.models import FoodDonation, PickupSchedule
from django.db.models import Count

def admin_dashboard(request):
    total_donations = FoodDonation.objects.count()
    pickup_status_counts = PickupSchedule.objects.values('pickup_status').annotate(count=Count('pickup_status'))
    return render(request, 'administration/admin_dashboard.html', {'total_donations': total_donations, 'pickup_status_counts': pickup_status_counts})

def pickup_management(request):
    pickups = PickupSchedule.objects.all()
    return render(request, 'administration/pickup_management.html', {'pickups': pickups})

def analytics(request):
    # Placeholder for analytics (e.g., donation trends)
    donation_counts = FoodDonation.objects.values('food_type').annotate(count=Count('food_type'))
    return render(request, 'administration/analytics.html', {'donation_counts': donation_counts})