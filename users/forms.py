from django import forms
from .models import CustomUser

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'mobile_number', 'password',
            'address', 'city', 'state', 'profile_picture', 'user_type'
        ]

