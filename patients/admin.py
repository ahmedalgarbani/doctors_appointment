from django.contrib import admin
 # Import Users model
from doctors.models import Doctor  # Import Doctor model


# # Ensure Users and Doctor have proper search_fields configured
# @admin.register(Users)
# class UsersAdmin(admin.ModelAdmin):
#     search_fields = ('username', 'email', 'full_name')  # Adjust fields as per the Users model



# @admin.register(Patients)
# class PatientsAdmin(admin.ModelAdmin):
#     list_display = ('full_name', 'user', 'birth_date', 'gender', 'phone_number', 'email', 'join_date')
#     list_filter = ('gender', 'join_date')
#     search_fields = ('full_name', 'phone_number', 'email', 'address')
#     ordering = ('-join_date',)
#     readonly_fields = ('join_date',)
#     fieldsets = (
#         (None, {
#             'fields': (
#                 'user',
#                 'full_name',
#                 'birth_date',
#                 'gender',
#                 'address',
#                 'phone_number',
#                 'email',
#                 'profile_picture',
#                 'notes'
#             )
#         }),
#         ('Metadata', {
#             'fields': ('join_date',),
#         }),
#     )

# @admin.register(Favourites)
# class FavouritesAdmin(admin.ModelAdmin):
#     list_display = ('user', 'doctor')
#     list_filter = ('user', 'doctor')
#     ordering = ('user', 'doctor')
#     autocomplete_fields = ('user', 'doctor')  # Ensure related admin classes have search_fields
#     fieldsets = (
#         (None, {
#             'fields': ('user', 'doctor')
#         }),
#     )