from django.shortcuts import render, redirect
from .forms import DonorRegistrationForm, DonationEntryForm
from core.models import Donor, FoodDonation, PickupSchedule, Receiver
from django.contrib.auth.hashers import check_password,make_password
from django.http import HttpResponseRedirect
import logging
from django.http import JsonResponse
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from .forms import DonorRegistrationForm, DonationEntryForm, ProfileUpdateForm
from core.models import Donor, DonorAddress, FoodDonation, PickupSchedule
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def donor_registration(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            donor = form.save()
            logger.debug("Donor registered: %s", donor.donor_id)
            return redirect('donors:donor_login')
    else:
        form = DonorRegistrationForm()
    return render(request, 'auth.html', {
        'form': form,
        'action': 'register',
        'user_type': 'donor',
        'active_tab': 'register'
    })

# ... (rest of the views remain unchanged)
def donor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            donor = Donor.objects.get(name=username)
            if check_password(password, donor.password):
                request.session['donor_id'] = donor.donor_id
                return redirect('donors:dashboard')
        except Donor.DoesNotExist:
            pass
    return render(request, 'auth.html', {'action': 'login', 'user_type': 'donor'})

def donor_dashboard(request):
    if 'donor_id' not in request.session:
        return redirect('donors:donor_login')
    donor = Donor.objects.get(donor_id=request.session['donor_id'])

    donations = FoodDonation.objects.filter(donor_id=donor)
    pending_pickups = PickupSchedule.objects.filter(donation_id__donor_id=donor, pickup_status='pending')

    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        action = request.POST.get('action')
        if schedule_id:
            pickup = PickupSchedule.objects.get(schedule_id=schedule_id)
            if action == 'accept':
                # Accept this receiver
                pickup.pickup_status = 'accepted'
                pickup.save()

                # Mark donation as reserved and store receiver
                donation = pickup.donation_id
                donation.status = 'reserved'
                donation.assigned_receiver = pickup.receiver_id
                donation.save()

                # Reject other pending pickups for this donation
                other_pickups = PickupSchedule.objects.filter(
                    donation_id=donation, pickup_status='pending'
                ).exclude(schedule_id=schedule_id)
                for op in other_pickups:
                    op.pickup_status = 'rejected'
                    op.save()
                    # Here you can send notification to receivers (WebSocket/Email)
                
            elif action == 'reject':
                pickup.pickup_status = 'rejected'
                pickup.save()
        return redirect('donors:dashboard')

    return render(request, 'dashboard.html', {
        'user_type': 'donor',
        'donations': donations,
        'pending_pickups': pending_pickups
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
            return redirect('donors:dashboard')
    else:
        form = DonationEntryForm()
    return render(request, 'donors/donation_entry.html', {'form': form})

def profile(request):
    if 'donor_id' not in request.session:
        return redirect('donors:donor_login')
    donor_id = request.session['donor_id']
    donor = Donor.objects.get(donor_id=donor_id)
    addresses = DonorAddress.objects.filter(donor_id=donor_id)
    if request.method == 'POST':
        if 'new_address' in request.POST:
            address = request.POST.get('new_address')
            DonorAddress.objects.create(donor_id=donor, address=address)
            return redirect('donors:profile')
        form = ProfileUpdateForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            return redirect('donors:profile')
    else:
        form = ProfileUpdateForm(instance=donor)
    return render(request, 'profile.html', {'user': donor, 'addresses': addresses, 'form': form})

def check_requests(request, donor_id):
    pickups = PickupSchedule.objects.filter(donation_id__donor_id=donor_id, pickup_status='pending')
    if pickups.exists():
        return JsonResponse({'message': 'New pickup request available.'})
    return JsonResponse({'message': ''})

def notify_receiver(receiver_id, schedule_id, status):
    pass  # Placeholder for WebSocket or real-time notification

def add_address(request):
    if 'donor_id' not in request.session:
        return redirect('donors:donor_login')
    if request.method == 'POST':
        address = request.POST.get('new_address')
        donor = Donor.objects.get(donor_id=request.session['donor_id'])
        DonorAddress.objects.create(donor_id=donor, address=address)
        return redirect('donors:profile')
    return redirect('donors:profile')

