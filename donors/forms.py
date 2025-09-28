from django import forms
from core.models import Donor, DonorAddress, FoodDonation

class DonorRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    addresses = forms.CharField(widget=forms.Textarea, required=False, help_text="Enter multiple addresses, one per line.")

    class Meta:
        model = Donor
        fields = ['name', 'contact', 'location_lat', 'location_long', 'password']

    def save(self, commit=True):
        donor = super().save(commit=False)
        if self.cleaned_data['password']:
            donor.password = self.cleaned_data['password']  # Handled in model save
        if commit:
            donor.save()
            # Handle multiple addresses
            if self.cleaned_data['addresses']:
                addresses = self.cleaned_data['addresses'].split('\n')
                for address in addresses:
                    if address.strip():
                        DonorAddress.objects.create(donor_id=donor, address=address.strip())  # Changed 'donor' to 'donor_id'
        return donor

class DonationEntryForm(forms.ModelForm):
    class Meta:
        model = FoodDonation
        fields = ['food_type', 'quantity', 'unit', 'expiry_time']