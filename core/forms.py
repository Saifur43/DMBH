from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

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
