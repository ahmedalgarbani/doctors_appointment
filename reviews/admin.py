from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Review, Offer
from django import forms
from HotelManagement.models import Hotel

class ReviewAdminForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        if request and hasattr(request, 'user') and request.user.user_type == 'hotel_manager':
            hotel = request.user.hotel
            self.fields['hotel'].initial = hotel
            self.fields['hotel'].disabled = True
            
            if 'created_by' in self.fields:
                self.fields['created_by'].initial = request.user
                self.fields['created_by'].disabled = True
            
            if 'updated_by' in self.fields:
                self.fields['updated_by'].initial = request.user
                self.fields['updated_by'].disabled = True

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    form = ReviewAdminForm
    list_display = ['user', 'hotel', 'rating', 'status', 'created_at']
    search_fields = ['user__username', 'review']
    list_filter = ['hotel', 'rating', 'status']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser or request.user.user_type == 'admin':
            return queryset
        elif request.user.user_type == 'hotel_manager':
            return queryset.filter(hotel__manager=request.user)
        return queryset.none()

    def has_delete_permission(self, request, obj=None):
        if not obj:
            return True
        if request.user.is_superuser or request.user.user_type == 'admin':
            return True
        return request.user.user_type == 'hotel_manager' and obj.hotel.manager == request.user

    def has_view_permission(self, request, obj=None):
        if not obj:
            return True
        if request.user.is_superuser or request.user.user_type == 'admin':
            return True
        return request.user.user_type == 'hotel_manager' and obj.hotel.manager == request.user

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Offer)
class ReviewOfferAdmin(admin.ModelAdmin):
    list_display = ['name', 'hotel', 'start_date', 'end_date', 'is_active']
    search_fields = ['name', 'description']
    list_filter = ['hotel', 'start_date', 'end_date', 'is_active']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser or request.user.user_type == 'admin':
            return queryset
        elif request.user.user_type == 'hotel_manager':
            return queryset.filter(hotel__manager=request.user)
        return queryset.none()

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.user_type in ['admin', 'hotel_manager']

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        if request.user.is_superuser or request.user.user_type == 'admin':
            return True
        return request.user.user_type == 'hotel_manager' and obj.hotel.manager == request.user

    def has_delete_permission(self, request, obj=None):
        if not obj:
            return True
        if request.user.is_superuser or request.user.user_type == 'admin':
            return True
        return request.user.user_type == 'hotel_manager' and obj.hotel.manager == request.user

    def has_view_permission(self, request, obj=None):
        if not obj:
            return True
        if request.user.is_superuser or request.user.user_type == 'admin':
            return True
        return request.user.user_type == 'hotel_manager' and obj.hotel.manager == request.user

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and request.user.user_type == 'hotel_manager':
            hotel = Hotel.objects.get(manager=request.user)
            form.base_fields['hotel'].queryset = Hotel.objects.filter(id=hotel.id)
            form.base_fields['hotel'].initial = hotel
            form.base_fields['hotel'].widget.attrs['readonly'] = True
            
            if 'updated_by' in form.base_fields:
                form.base_fields['updated_by'].initial = request.user
                form.base_fields['updated_by'].widget.attrs['readonly'] = True
                form.base_fields['updated_by'].required = False
            
            if 'created_by' in form.base_fields:
                form.base_fields['created_by'].initial = request.user
                form.base_fields['created_by'].widget.attrs['readonly'] = True
                form.base_fields['created_by'].required = False
        return form

    def save_model(self, request, obj, form, change):
        if not change:  
            if request.user.user_type == 'hotel_manager':
                obj.hotel = request.user.hotel
        super().save_model(request, obj, form, change)