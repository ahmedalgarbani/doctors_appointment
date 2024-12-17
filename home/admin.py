from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import *

# Custom Form for SettingAdmin
class SettingAdminForm(forms.ModelForm):
    class Meta:
        model = Setting
        fields = '__all__'
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    form = SettingAdminForm  
    list_display = (
        'site_name', 
        'default_currency', 
        'currency_icon', 
        'currency_Icon_position', 
        'logo_preview', 
        'favicon_preview',
        'seo_title',
    )
    list_filter = ('currency_Icon_position', 'default_language')
    search_fields = ('site_name', 'default_currency', 'seo_title')
    readonly_fields = ('logo_preview', 'favicon_preview', 'footer_logo_preview')

    fieldsets = (
        ('Site Information', {
            'fields': (
                'site_name', 'description', 'default_currency', 
                'default_language', 'color', 'currency_icon', 'currency_Icon_position'
            )
        }),
        ('Logos & Icons', {
            'fields': ('logo', 'logo_preview', 'favicon', 'favicon_preview', 'footer_logo', 'footer_logo_preview'),
        }),
        ('SEO Settings', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords'),
        }),
        ('Google Map', {
            'fields': ('google_map_link',),
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:50px;"/>', obj.logo.url)
        return "No Logo"
    logo_preview.short_description = "Logo Preview"

    def favicon_preview(self, obj):
        if obj.favicon:
            return format_html('<img src="{}" style="height:20px;"/>', obj.favicon.url)
        return "No Favicon"
    favicon_preview.short_description = "Favicon Preview"

    def footer_logo_preview(self, obj):
        if obj.footer_logo:
            return format_html('<img src="{}" style="height:50px;"/>', obj.footer_logo.url)
        return "No Footer Logo"
    footer_logo_preview.short_description = "Footer Logo Preview"









@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'header_icon', 'main_image')
    search_fields = ('title',)
@admin.register(TermsConditions)
class TermsConditionsAdmin(admin.ModelAdmin):
    search_fields = ('content',)


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    search_fields = ('content',)


class WorkStepInline(admin.TabularInline):
    model = WorkStep
    extra = 1 
    fields = ('order', 'title', 'description', 'icon', 'show_at_home')
    readonly_fields = ('order',) 
    can_delete = False  

class WorkSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'sub_title', 'main_image')  
    search_fields = ('title', 'sub_title')  
    list_filter = ('title',)  
    inlines = [WorkStepInline] 
    ordering = ('title',) 
    fieldsets = (
        (None, {
            'fields': ('title', 'sub_title', 'main_image')
        }),
    )  
    

class WorkStepAdmin(admin.ModelAdmin):
    list_display = ('work_section', 'order', 'title', 'show_at_home') 
    search_fields = ('title', 'description')  
    list_filter = ('work_section', 'show_at_home')  
    readonly_fields = ('order',)  
    ordering = ('work_section', 'order') 
    list_editable = ('show_at_home',) 

    def save_model(self, request, obj, form, change):
        """Override save_model to handle automatic order setting before saving"""
        if not obj.order:  
            max_order = WorkStep.objects.filter(work_section=obj.work_section).aggregate(Max('order'))['order__max']
            obj.order = (max_order or 0) + 1  
        super().save_model(request, obj, form, change)


class AppSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'sub_title', 'qr_title', 'show_at_home', 'app_photo') 
    search_fields = ('title', 'qr_title')  
    list_filter = ('show_at_home',)  
    ordering = ('title',)  
    
    def get_image_preview(self, obj):
        if obj.app_photo:
            return f'<img src="{obj.app_photo.url}" style="width: 50px; height: auto;" />'
        return '-'
    get_image_preview.allow_tags = True
    get_image_preview.short_description = 'App Photo Preview'

    fieldsets = (
        (None, {
            'fields': ('title', 'sub_title', 'qr_title', 'qr_image', 'google_play_icon', 'google_play_url', 'apple_store_icon', 'apple_store_url', 'app_photo', 'show_at_home')
        }),
    )
    
    readonly_fields = ('get_image_preview',)

from django.contrib import admin
from .models import FAQSection, Question
from django.db.models import Max


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('order', 'question', 'answer', 'show_at_home')  
    readonly_fields = ('order',) 
    can_delete = False  


class FAQSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'sub_title', 'show_at_home', 'main_image_preview')
    search_fields = ('title', 'sub_title')  
    list_filter = ('show_at_home',) 
    inlines = [QuestionInline]  
    ordering = ('title',)  
    fieldsets = (
        (None, {
            'fields': ('title', 'sub_title', 'main_image', 'show_at_home')
        }),
    )

    def main_image_preview(self, obj):
        if obj.main_image:
            return f'<img src="{obj.main_image.url}" style="width: 50px; height: auto;" />'
        return '-'
    main_image_preview.allow_tags = True
    main_image_preview.short_description = 'Main Image Preview'


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('faq_section', 'order', 'question', 'show_at_home') 
    search_fields = ('question', 'answer')  
    list_filter = ('faq_section', 'show_at_home') 
    readonly_fields = ('order',) 
    ordering = ('faq_section', 'order')  
    list_editable = ('show_at_home',)  

    def save_model(self, request, obj, form, change):
        """Override save_model to handle automatic order setting before saving"""
        if not obj.order:
            max_order = Question.objects.filter(faq_section=obj.faq_section).aggregate(Max('order'))['order__max']
            obj.order = (max_order or 0) + 1
        super().save_model(request, obj, form, change)



class TestimonialInline(admin.TabularInline):
    model = Testimonial
    extra = 1
    fields = ('main_image', 'review', 'name', 'country', 'order', 'show_at_home')
    readonly_fields = ('order',)
    can_delete = True


class TestimonialSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'sub_title', 'status')
    search_fields = ('title', 'sub_title')
    list_filter = ('status',)
    inlines = [TestimonialInline]
    ordering = ('title',)

    fieldsets = (
        (None, {
            'fields': ('title', 'sub_title', 'status')
        }),
    )


class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('testimonial', 'order', 'name', 'country', 'show_at_home')
    search_fields = ('name', 'review')
    list_filter = ('testimonial', 'show_at_home')
    readonly_fields = ('order',)
    ordering = ('testimonial', 'order')
    list_editable = ('show_at_home',)

    def save_model(self, request, obj, form, change):
        if not obj.order:
            max_order = Testimonial.objects.filter(testimonial=obj.testimonial).aggregate(Max('order'))['order__max']
            obj.order = (max_order or 0) + 1
        super().save_model(request, obj, form, change)



class PartnersSectionAdmin(admin.ModelAdmin):
    list_display = ( 'pertner_image', 'show_at_home')
    list_filter = ('show_at_home',)

    fieldsets = (
        (None, {
            'fields': ( 'pertner_image', 'show_at_home')
        }),
    )


@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'link', 'icon', 'status') 
    list_filter = ('status',) 
    search_fields = ('name', 'link', 'icon')  
    ordering = ('name',)  
    fieldsets = (
        (None, {
            'fields': ('name', 'link', 'icon', 'status') 
        }),
    )

admin.site.register(PartnersSection, PartnersSectionAdmin)
admin.site.register(AppSection, AppSectionAdmin)
admin.site.register(WorkSection, WorkSectionAdmin)
admin.site.register(WorkStep, WorkStepAdmin)
admin.site.register(FAQSection, FAQSectionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(TestimonialSection, TestimonialSectionAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
