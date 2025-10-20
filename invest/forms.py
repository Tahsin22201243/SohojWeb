from django import forms
from django.contrib.auth.models import User
from .models import Business, Campaign, Investment, Update, ContactMessage, Profile
from invest import models

class BusinessApplicationForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'description', 'location', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe your business'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website (optional)'}),
        }

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'description', 'target_amount', 'min_investment', 'start_date', 'end_date', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campaign Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Campaign Description'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Target Amount'}),
            'min_investment': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum Investment'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Investment Amount'}),
        }

class UpdateForm(forms.ModelForm):
    # attachments are handled manually in the template via a plain file input
    class Meta:
        model = Update
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Update Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control rich-text', 'placeholder': 'Update Content'}),
        }


class UpdateEditForm(forms.ModelForm):
    class Meta:
        model = Update
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Update Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control rich-text', 'placeholder': 'Update Content'}),
        }

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message'}),
        }

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm")
        if password and confirm and password != confirm:
            self.add_error('confirm', "Passwords do not match.")

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'phone', 'address', 'avatar', 'bio', 'bank_account', 'kyc_type', 'kyc_document', 'birthdate', 'country', 'city', 'postal_code']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Short bio', 'rows': 3}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank account (optional)'}),
            'kyc_type': forms.Select(attrs={'class': 'form-select'}),
            'kyc_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'birthdate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }