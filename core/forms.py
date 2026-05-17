from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ContactMessage

class BuyerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': '+1234567890'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.IS_BUYER
        if commit:
            user.save()
        return user

class ContactForm(forms.ModelForm):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone (optional)'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Your message...'}))

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']

    def save(self, commit=True):
        return ContactMessage.objects.create(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data.get('phone', ''),
            message=self.cleaned_data['message']
        )
