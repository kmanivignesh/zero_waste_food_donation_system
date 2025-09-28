from django.shortcuts import render, redirect
from .forms import DonorRegistrationForm, DonationEntryForm
from core.models import Donor, FoodDonation, PickupSchedule, Receiver
from django.contrib.auth.hashers import check_password
from django.http import HttpResponseRedirect
import logging

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
            logger.debug("Form is valid: %s", form.cleaned_data)
            form.save()
            logger.debug("Donor saved successfully")
            return redirect('donors:donor_login')
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
        logger.debug("No donor_id in session, redirecting to login")
        return redirect('donors:donor_login')
    
    donor_id = request.session['donor_id']
    donations = FoodDonation.objects.filter(donor_id=donor_id)
    scheduled_pickups = PickupSchedule.objects.filter(donation_id__donor_id=donor_id)
    logger.debug("Scheduled pickups count: %d, Details: %s", scheduled_pickups.count(), list(scheduled_pickups.values('schedule_id', 'donation_id', 'receiver_id', 'pickup_status')))
    
    if request.method == 'POST':
        schedule_id = request.POST.get('pickup_id')  # Ensure this matches the form
        action = request.POST.get('action')
        if schedule_id and action:
            pickup = PickupSchedule.objects.get(schedule_id=schedule_id)  # Use schedule_id
            if action == 'accept':
                pickup.pickup_status = 'accepted'
                pickup.donation_id.status = 'reserved'
            elif action == 'reject':
                pickup.pickup_status = 'rejected'
                pickup.donation_id.status = 'available'
            pickup.save()
            logger.debug("Pickup %s updated to %s", schedule_id, pickup.pickup_status)
            return redirect('donors:donor_dashboard')
    
    return render(request, 'donors/donor_dashboard.html', {
        'donations': donations,
        'scheduled_pickups': scheduled_pickups
    })

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
            receivers = Receiver.objects.all()
            logger.debug("Found %d receivers", receivers.count())
            if receivers.exists():
                for receiver in receivers:
                    distance = donation.donor_id.calculate_distance(receiver.location_lat, receiver.location_long)
                    priority = (1 - 0.5) * (1 / max(distance, 1))
                    pickup = PickupSchedule.objects.create(
                        donation_id=donation,
                        receiver_id=receiver,
                        priority_score=priority,
                        scheduled_time=donation.expiry_time,
                        pickup_status='pending'
                    )
                    logger.debug("Created pickup: schedule_id=%s, Receiver=%s, Distance=%f", pickup.schedule_id, receiver.name, distance)
            else:
                logger.debug("No receivers available to schedule pickup")
            return redirect('donors:donor_dashboard')
    else:
        form = DonationEntryForm()
    return render(request, 'donors/donation_entry.html', {'form': form})






# ... (other views like donor_registration, donor_login, donor_logout remain the same)



