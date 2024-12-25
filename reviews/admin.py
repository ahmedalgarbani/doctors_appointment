from django.contrib import admin
from .models import Review

<<<<<<< HEAD
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'hospital', 'doctor', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating', 'hospital', 'doctor')
    search_fields = ('user__username', 'hospital__name', 'doctor__name', 'review')
    ordering = ['-created_at']
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(status=True)
        self.message_user(request, "تمت الموافقة على المراجعات المحددة.")
    approve_reviews.short_description = "موافقة على المراجعات"

    def reject_reviews(self, request, queryset):
        queryset.update(status=False)
        self.message_user(request, "تم رفض المراجعات المحددة.")
    reject_reviews.short_description = "رفض المراجعات"

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return self.readonly_fields + ('user', 'created_at')
        return self.readonly_fields

    readonly_fields = ('created_at',) 
=======

admin.site.register(Review)
>>>>>>> 17a6cc346d6933bc45c5346f29d0bec0ec6e5923
