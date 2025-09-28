from django import forms
from django.contrib.auth.hashers import make_password
from core.models import Donor, DonorAddress, FoodDonation

from django import forms
from core.models import Donor, DonorAddress

class DonorRegistrationForm(forms.ModelForm):
    addresses = forms.CharField(widget=forms.Textarea, required=False, help_text="Enter addresses (one per line)")

    class Meta:
        model = Donor
        fields = ['name', 'contact', 'location_lat', 'location_long', 'password']

    def save(self, *args, **kwargs):
        donor = super().save(commit=False)
        donor.password = make_password(self.cleaned_data['password'])  # Hash the password
        donor.save()

        # Process addresses
        if self.cleaned_data['addresses']:
            address_list = self.cleaned_data['addresses'].strip().split('\n')
            for address in address_list:
                if address.strip():
                    DonorAddress.objects.create(
                        donor_id=donor,  # Use donor_id instead of donor
                        address=address.strip()
                    )

        return donor
    
class DonationEntryForm(forms.ModelForm):
    class Meta:
        model = FoodDonation
        fields = ['food_type', 'quantity', 'unit', 'expiry_time']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ['name', 'contact', 'location_lat', 'location_long']
        # Exclude password as it's sensitive and not meant for update via form