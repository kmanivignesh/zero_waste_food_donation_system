from django import forms
from core.models import Receiver, ReceiverAddress

class ReceiverRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    addresses = forms.CharField(widget=forms.Textarea, required=False, help_text="Enter multiple addresses, one per line.")

    class Meta:
        model = Receiver
        fields = ['name', 'contact', 'capacity', 'location_lat', 'location_long', 'password']

    def save(self, commit=True):
        receiver = super().save(commit=False)
        if self.cleaned_data['password']:
            receiver.password = self.cleaned_data['password']  # Handled in model save
        if commit:
            receiver.save()
            if self.cleaned_data['addresses']:
                addresses = self.cleaned_data['addresses'].split('\n')
                for address in addresses:
                    if address.strip():
                        ReceiverAddress.objects.create(receiver_id=receiver, address=address.strip())  # Changed 'receiver' to 'receiver_id'
        return receiver
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Receiver
        fields = ['name', 'contact', 'location_lat', 'location_long']
        # Exclude password as it's sensitive and not meant for update via form   