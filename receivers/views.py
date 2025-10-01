from django.contrib import messages
from .forms import ReceiverRegistrationForm, ProfileUpdateForm , CapacityUpdateForm
from core.models import Receiver, FoodDonation, PickupSchedule, ReceiverAddress
from django.http import JsonResponse
from ML_Model.ml_model import priority_model, food_type_encoder, scaler
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from core.models import Receiver, FoodDonation, PickupSchedule, ReceiverAddress
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def receiver_registration(request):
    if request.method == 'POST':
        form = ReceiverRegistrationForm(request.POST)
        if form.is_valid():
            receiver = form.save()
            logger.debug("Receiver registered: %s", receiver.receiver_id)
            return redirect('receivers:receiver_login')
    else:
        form = ReceiverRegistrationForm()
    return render(request, 'auth.html', {
        'form': form,
        'action': 'register',
        'user_type': 'receiver',
        'active_tab': 'register'
    })

# ... (rest of the views remain unchanged)
# ... (rest of the views remain unchanged)
def receiver_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            receiver = Receiver.objects.get(name=username)
            if check_password(password, receiver.password):
                request.session['receiver_id'] = receiver.receiver_id
                return redirect('receivers:dashboard')
        except Receiver.DoesNotExist:
            pass
    return render(request, 'auth.html', {'action': 'login', 'user_type': 'receiver'})

def receiver_dashboard(request):
    if 'receiver_id' not in request.session:
        return redirect('receivers:receiver_login')
    
    receiver = Receiver.objects.get(receiver_id=request.session['receiver_id'])
    available_donations = FoodDonation.objects.filter(status='available')

    # Update priority for each donation for this receiver
    for donation in available_donations:
        donation.calculate_priority_ml(
            receiver_capacity=receiver.capacity,
            receiver_lat=receiver.location_lat,
            receiver_long=receiver.location_long
        )

    accepted_pickups = PickupSchedule.objects.filter(receiver_id=receiver)

    # Handle capacity update
    if request.method == 'POST' and 'update_capacity' in request.POST:
        form = CapacityUpdateForm(request.POST, instance=receiver)
        if form.is_valid():
            form.save()
            messages.success(request, "Capacity updated successfully!")
            return redirect('receivers:dashboard')
    else:
        form = CapacityUpdateForm(instance=receiver)

    return render(request, 'dashboard.html', {
        'user_type': 'receiver',
        'available_donations': available_donations,
        'accepted_pickups': accepted_pickups,
        'capacity_form': form  # Pass form to template
    })



def profile(request):
    if 'receiver_id' not in request.session:
        return redirect('receivers:receiver_login')
    receiver_id = request.session['receiver_id']
    receiver = Receiver.objects.get(receiver_id=receiver_id)
    addresses = ReceiverAddress.objects.filter(receiver_id=receiver_id)
    if request.method == 'POST':
        if 'new_address' in request.POST:
            address = request.POST.get('new_address')
            ReceiverAddress.objects.create(receiver_id=receiver, address=address)
            return redirect('receivers:profile')
        form = ProfileUpdateForm(request.POST, instance=receiver)
        if form.is_valid():
            form.save()
            return redirect('receivers:profile')
    else:
        form = ProfileUpdateForm(instance=receiver)
    return render(request, 'profile.html', {'user': receiver, 'addresses': addresses, 'form': form})

def check_notification(request, receiver_id):
    pickups = PickupSchedule.objects.filter(receiver_id__receiver_id=receiver_id)
    for pickup in pickups:
        if pickup.pickup_status == 'accepted':
            return JsonResponse({'message': f'Pickup {pickup.schedule_id} successfully allocated.'})
        elif pickup.pickup_status == 'rejected':
            return JsonResponse({'message': f'Pickup {pickup.schedule_id} allocated to another receiver.'})
    return JsonResponse({'message': ''})

def schedule_pickup(request, donation_id):
    if 'receiver_id' not in request.session:
        return redirect('receivers:receiver_login')
    if request.method == 'POST':
        receiver = Receiver.objects.get(receiver_id=request.session['receiver_id'])
        donation = FoodDonation.objects.get(donation_id=donation_id)

        # ML-based priority
        priority = donation.calculate_priority_ml(
            receiver_capacity=receiver.capacity,
            receiver_lat=receiver.location_lat,
            receiver_long=receiver.location_long
        )

        PickupSchedule.objects.create(
            donation_id=donation,
            receiver_id=receiver,
            priority_score=priority,
            scheduled_time=donation.expiry_time,
            pickup_status='pending'
        )
        logger.debug("Pickup scheduled for donation %s by receiver %s", donation_id, receiver.receiver_id)
        return redirect('receivers:dashboard')
    return redirect('receivers:dashboard')
