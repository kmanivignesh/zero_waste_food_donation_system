from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .forms import ReceiverRegistrationForm
from core.models import Receiver, FoodDonation, PickupSchedule
import logging
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .forms import ReceiverRegistrationForm, ProfileUpdateForm
from core.models import Receiver, FoodDonation, PickupSchedule, ReceiverAddress
import logging
from django.http import JsonResponse



logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from .forms import ReceiverRegistrationForm, ProfileUpdateForm
from core.models import Receiver, FoodDonation, PickupSchedule, ReceiverAddress
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from .forms import ReceiverRegistrationForm, ProfileUpdateForm
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
                return redirect('receivers:dashboard')
    return render(request, 'dashboard.html', {'user_type': 'receiver', 'available_donations': available_donations, 'scheduled_pickups': scheduled_pickups})

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
        distance = donation.donor_id.calculate_distance(receiver.location_lat, receiver.location_long)
        priority = (1 - 0.5) * (1 / max(distance, 1))
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