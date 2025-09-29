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


def admin_logout(request):
    request.session.flush()
    return redirect("admin_login")

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if "admin_id" not in request.session:
            return redirect("admin_login")
        return view_func(request, *args, **kwargs)
    return wrapper



# --- Donors ---
@admin_required
def donors_list(request):
    donors = Donor.objects.all()
    return render(request, "administration/donors.html", {"donors": donors})

# --- Receivers ---
@admin_required
def receivers_list(request):
    receivers = Receiver.objects.all()
    return render(request, "administration/receivers.html", {"receivers": receivers})

# --- Donations ---
@admin_required
def donations_list(request):
    donations = FoodDonation.objects.all()
    return render(request, "administration/donations.html", {"donations": donations})

# --- Pickups ---
@admin_required
def pickups_list(request):
    pickups = PickupSchedule.objects.all()
    return render(request, "administration/pickups.html", {"pickups": pickups})

# --- Analytics ---
@admin_required
def analytics_view(request):
    donations_by_type = (
        FoodDonation.objects.values("food_type").order_by("food_type")
    )
    return render(request, "administration/analytics.html", {
        "donations_by_type": donations_by_type
    })
