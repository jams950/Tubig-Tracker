from django import forms
from .models import Complaint, ComplaintPhoto, Report, User


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'title',
            'description',
            'area',
            'barangay',
            'purok',
            'latitude',
            'longitude',
            'photo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True
        self.fields['area'].required = True  # make sure area is mandatory

class ComplaintPhotoForm(forms.ModelForm):
    class Meta:
        model = ComplaintPhoto
        fields = ['photo']


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")


class ReportForm(forms.ModelForm):
    photo = forms.ImageField(required=False)  # Optional photo upload

    class Meta:
        model = Report
        fields = ['title', 'description', 'latitude', 'longitude', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter report title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the issue'
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make latitude and longitude required
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('latitude')
        lng = cleaned_data.get('longitude')

        if not lat or not lng:
            raise forms.ValidationError("Please select a location on the map before submitting.")

        return cleaned_data