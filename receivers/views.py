from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .forms import ReceiverRegistrationForm
from core.models import Receiver, FoodDonation, PickupSchedule
import logging

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
        logger.debug("No receiver_id in session, redirecting to login")
        return redirect('receivers:receiver_login')
    
    receiver_id = request.session['receiver_id']
    logger.debug("Fetching data for receiver_id: %s", receiver_id)
    available_donations = FoodDonation.objects.filter(status='available')
    scheduled_pickups = PickupSchedule.objects.filter(receiver_id__receiver_id=receiver_id)
    logger.debug("Scheduled pickups count: %d, Details: %s", scheduled_pickups.count(), list(scheduled_pickups.values('schedule_id', 'donation_id', 'receiver_id', 'pickup_status')))
    
    if request.method == 'POST':
        schedule_id = request.POST.get('pickup_id')  # Ensure this matches the form
        action = request.POST.get('action')
        if schedule_id and action:
            pickup = PickupSchedule.objects.get(schedule_id=schedule_id)  # Use schedule_id
            if action == 'confirm':
                pickup.pickup_status = 'confirmed'
            elif action == 'cancel':
                pickup.pickup_status = 'cancelled'
                pickup.donation_id.status = 'available'
            pickup.save()
            logger.debug("Pickup %s updated to %s", schedule_id, pickup.pickup_status)
            return redirect('receivers:receiver_dashboard')
    
    return render(request, 'receivers/receiver_dashboard.html', {
        'available_donations': available_donations,
        'scheduled_pickups': scheduled_pickups
    })