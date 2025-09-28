from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .forms import ReceiverRegistrationForm
from core.models import Receiver, FoodDonation, PickupSchedule
import logging
from django.contrib import messages

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def receiver_registration(request):
    if request.method == 'POST':
        form = ReceiverRegistrationForm(request.POST)
        if form.is_valid():
            logger.debug("Form is valid: %s", form.cleaned_data)
            form.save()
            logger.debug("Receiver saved successfully")
            return redirect('receivers:receiver_login')  # Ensure this is correct
    else:
        form = ReceiverRegistrationForm()
    return render(request, 'receivers/receiver_registration.html', {'form': form})

def receiver_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            receiver = Receiver.objects.get(name=username)
            if check_password(password, receiver.password):
                request.session['receiver_id'] = receiver.receiver_id
                logger.debug("Login successful for receiver_id: %s", receiver.receiver_id)
                return redirect('receivers:receiver_dashboard')
        except Receiver.DoesNotExist:
            logger.debug("Receiver not found: %s", username)
    return render(request, 'receivers/login.html', {'error': 'Invalid credentials' if request.method == 'POST' else None})

def receiver_logout(request):
    try:
        del request.session['receiver_id']
        logger.debug("Logout successful")
    except KeyError:
        pass
    return redirect('receivers:receiver_login')

def receiver_dashboard(request):
    if 'receiver_id' not in request.session:
        return redirect('receivers:receiver_login')
    
    receiver_id = request.session['receiver_id']
    available_donations = FoodDonation.objects.filter(status='available')
    scheduled_pickups = PickupSchedule.objects.filter(receiver_id__receiver_id=receiver_id)
    
    if request.method == 'POST':
        if 'schedule_pickup' in request.POST:
            donation_id = request.POST.get('donation_id')
            if donation_id:
                donation = FoodDonation.objects.get(donation_id=donation_id)
                distance = donation.donor_id.calculate_distance(
                    Receiver.objects.get(receiver_id=receiver_id).location_lat,
                    Receiver.objects.get(receiver_id=receiver_id).location_long
                )
                priority = (1 - 0.5) * (1 / max(distance, 1))
                PickupSchedule.objects.create(
                    donation_id=donation,
                    receiver_id=Receiver.objects.get(receiver_id=receiver_id),
                    priority_score=priority,
                    scheduled_time=donation.expiry_time,
                    pickup_status='pending'
                )
                logger.debug("Pickup scheduled for donation %s by receiver %s", donation_id, receiver_id)
                return redirect('receivers:receiver_dashboard')
    
    return render(request, 'receivers/receiver_dashboard.html', {
        'available_donations': available_donations,
        'scheduled_pickups': scheduled_pickups,
        'receiver_id': receiver_id
    })

from django.http import JsonResponse
from core.models import PickupSchedule

def check_notification(request, receiver_id):
    pickups = PickupSchedule.objects.filter(receiver_id__receiver_id=receiver_id)
    for pickup in pickups:
        if pickup.pickup_status == 'accepted':
            return JsonResponse({'message': f'Pickup {pickup.schedule_id} successfully allocated.'})
        elif pickup.pickup_status == 'rejected':
            return JsonResponse({'message': f'Pickup {pickup.schedule_id} allocated to another receiver.'})
    return JsonResponse({'message': ''})