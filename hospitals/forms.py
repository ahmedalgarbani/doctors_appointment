from django import forms
from doctors.models import Doctor
from notifications.models import Notifications
from users.models import CustomUser
from django.contrib.auth import get_user_model

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'hospitals': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'specialty': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'sub_title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_at_home': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



class NotificationForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),  # استخدام CustomUser
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="حدد المستلمين",
    )
    send_to_all = forms.BooleanField(
        required=False,
        label="إرسال لجميع المستخدمين"
    )

    class Meta:
        model = Notifications
        fields = ['message', 'notification_type', 'recipients', 'send_to_all']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'notification_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        send_to_all = cleaned_data.get('send_to_all')
        recipients = cleaned_data.get('recipients')

        if not send_to_all and not recipients:
            raise forms.ValidationError("يرجى تحديد المستلمين أو اختيار إرسال للجميع.")

        return cleaned_data
