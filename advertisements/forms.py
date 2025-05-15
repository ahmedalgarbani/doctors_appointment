from django import forms
from .models import Advertisement, AdvertisementImage

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput)
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'description', 'image', 'image2', 'image3', 'image4', 'start_date', 'end_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل عنوان الإعلان'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'أدخل وصف الإعلان هنا...', 'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image3': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image4': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select form-control'}),
        }


class AdvertisementImageForm(forms.ModelForm):
    class Meta:
        model = AdvertisementImage
        fields = ['image', 'order']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '10'}),
        }
