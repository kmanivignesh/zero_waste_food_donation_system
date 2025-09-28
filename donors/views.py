from django.shortcuts import render, redirect
from .forms import DonorRegistrationForm, DonationEntryForm
from core.models import Donor, FoodDonation, PickupSchedule, Receiver
from django.contrib.auth.hashers import check_password,make_password
from django.http import HttpResponseRedirect
import logging
from django.http import JsonResponse
from django.contrib import messages


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def donor_registration(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            logger.debug("Form is valid: %s", form.cleaned_data)
            form.save()
            logger.debug("Donor saved successfully")
            return redirect('donors:donor_dashboard')
        else:
            logger.debug("Form errors: %s", form.errors)
    else:
        form = DonorRegistrationForm()
    return render(request, 'donors/donor_registration.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .forms import DonorRegistrationForm, DonationEntryForm
from core.models import Donor, FoodDonation, PickupSchedule, Receiver
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def donor_registration(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.password = make_password(form.cleaned_data['password'])
            donor.save()
            logger.debug("Donor registered: %s", donor.donor_id)
            return redirect('donors:donor_login')  # Use namespace here
    else:
        form = DonorRegistrationForm()
    return render(request, 'donors/donor_registration.html', {'form': form})

def donor_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            donors = Donor.objects.filter(name=username)  # Get all matching donors
            if donors.exists():
                donor = donors.first()  # Take the first match (temporary fix)
                if check_password(password, donor.password):
                    request.session['donor_id'] = donor.donor_id
                    logger.debug("Login successful for donor_id: %s", donor.donor_id)
                    return redirect('donors:donor_dashboard')
                else:
                    logger.debug("Invalid password for username: %s", username)
            else:
                logger.debug("Donor not found: %s", username)
        except Exception as e:
            logger.debug("Error in login: %s", str(e))
    return render(request, 'donors/login.html', {'error': 'Invalid credentials' if request.method == 'POST' else None})

def donor_logout(request):
    try:
        del request.session['donor_id']
        logger.debug("Logout successful")
    except KeyError:
        pass
    return redirect('donors:donor_login')

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .forms import DonorRegistrationForm, DonationEntryForm
from core.models import Donor, FoodDonation, PickupSchedule, Receiver
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ... (other views like donor_registration, donor_login, donor_logout)
def donor_dashboard(request):
    if 'donor_id' not in request.session:
        return redirect('donors:donor_login')
    
    donor_id = request.session['donor_id']
    donations = FoodDonation.objects.filter(donor_id=donor_id)
    scheduled_pickups = PickupSchedule.objects.filter(donation_id__donor_id=donor_id, pickup_status='pending')
    
    if request.method == 'POST':
        schedule_id = request.POST.get('pickup_id')
        action = request.POST.get('action')
        if schedule_id and action:
            pickup = PickupSchedule.objects.get(schedule_id=schedule_id)
            if action == 'accept':
                pickup.pickup_status = 'accepted'
                pickup.donation_id.status = 'reserved'
                pickup.save()
                logger.debug("Donor accepted pickup %s for receiver %s", schedule_id, pickup.receiver_id.name)
                # Notify accepting receiver
                notify_receiver(pickup.receiver_id.receiver_id, schedule_id, 'accepted')
                # Reject other pending pickups for the same donation
                other_pickups = PickupSchedule.objects.filter(donation_id=pickup.donation_id, pickup_status='pending').exclude(schedule_id=schedule_id)
                for other_pickup in other_pickups:
                    other_pickup.pickup_status = 'rejected'
                    other_pickup.save()
                    notify_receiver(other_pickup.receiver_id.receiver_id, schedule_id, 'rejected')
            elif action == 'reject':
                pickup.pickup_status = 'rejected'
                pickup.save()
                logger.debug("Donor rejected pickup %s", schedule_id)
            return redirect('donors:donor_dashboard')
    
    return render(request, 'donors/donor_dashboard.html', {
        'donations': donations,
        'scheduled_pickups': scheduled_pickups,
        'donor_id': donor_id
    })

def notify_receiver(receiver_id, schedule_id, status):
    # This is a placeholder for real-time notification (e.g., WebSocket or polling)
    # For now, we'll simulate it with a comment
    pass  # Implement with JavaScript or WebSocket later

def donation_entry(request):
    if 'donor_id' not in request.session:
        return redirect('donors:donor_login')
    if request.method == 'POST':
        form = DonationEntryForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor_id = Donor.objects.get(donor_id=request.session['donor_id'])
            donation.save()
            logger.debug("Donation saved: ID=%s, Donor=%s", donation.donation_id, donation.donor_id.donor_id)
            return redirect('donors:donor_dashboard')
    else:
        form = DonationEntryForm()
    return render(request, 'donors/donation_entry.html', {'form': form})

def check_requests(request, donor_id):
    pickups = PickupSchedule.objects.filter(donation_id__donor_id=donor_id, pickup_status='pending')
    if pickups.exists():
        return JsonResponse({'message': 'New pickup request available.'})
    return JsonResponse({'message': ''})