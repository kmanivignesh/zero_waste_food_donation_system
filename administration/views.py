# administration/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from core.models import Donor, Receiver, FoodDonation, PickupSchedule, MLPredictions
from .models import Admin
from .forms import AdminLoginForm
from django.db.models import Count

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                admin_user = Admin.objects.get(username=username)
                if check_password(password, admin_user.password):
                    request.session['admin_id'] = admin_user.id
                    return redirect('admin_dashboard')
                else:
                    form.add_error(None, "Invalid password")
            except Admin.DoesNotExist:
                form.add_error(None, "Admin not found")
    else:
        form = AdminLoginForm()
    return render(request, 'administration/login.html', {'form': form})


def admin_dashboard(request):
    if not request.session.get('admin_id'):
        return redirect('admin_login')

    donors_count = Donor.objects.count()
    receivers_count = Receiver.objects.count()
    donations_count = FoodDonation.objects.count()
    pickups_count = PickupSchedule.objects.count()

    # Top donors by number of donations
    top_donors = Donor.objects.annotate(num_donations=Count('fooddonation')).order_by('-num_donations')[:5]

    # Top receivers by assigned donations
    top_receivers = Receiver.objects.annotate(num_received=Count('fooddonation')).order_by('-num_received')[:5]

    context = {
        'donors_count': donors_count,
        'receivers_count': receivers_count,
        'donations_count': donations_count,
        'pickups_count': pickups_count,
        'top_donors': top_donors,
        'top_receivers': top_receivers
    }

    return render(request, 'administration/dashboard.html', context)

