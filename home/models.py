from django.db import models
import os
from PIL import Image
from django.core.exceptions import ValidationError
# Create your models here.



class HomeBanner(models.Model):
    title = models.CharField(max_length=255)  
    subtitle = models.TextField(blank=True, null=True)  
    header_icon = models.ImageField(upload_to='home/components/homebanner/icons/',      blank=True, null=True)  
    main_image = models.ImageField(upload_to='home/components/homebanner/', blank=True, null=True)  
    sub_image1 = models.ImageField(upload_to='home/components/homebanner/', blank=True, null=True)  
    sub_image2 = models.ImageField(upload_to='home/components/homebanner/', blank=True, null=True)  
    sub_image3 = models.ImageField(upload_to='home/components/homebanner/', blank=True, null=True)  

    def __str__(self):
        return self.title
   
class WorkSection(models.Model):
    title = models.CharField(max_length=150)
    sub_title = models.CharField(max_length=255)
    main_image = models.ImageField(upload_to='home/components/work/') 
 

    def __str__(self):
        return f"{self.title}: {self.sub_title}"   
    
class WorkStep(models.Model):
    work_section = models.ForeignKey(WorkSection,on_delete=models.CASCADE,related_name='steps')
    order = models.PositiveIntegerField()  
    title = models.CharField(max_length=100)  
    description = models.TextField() 
    icon = models.ImageField(upload_to='home/components/work/icons/')
    show_at_home = models.BooleanField(default=True) 
    
    class Meta:
        ordering = ['order'] 

    def __str__(self):
        return f"Step {self.order}: {self.title}"
    def save(self, *args, **kwargs):
        if not self.order: 
            max_order = WorkStep.objects.filter(work_section=self.work_section).aggregate(models.Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)



class AppSection(models.Model):
    title = models.CharField(max_length=100)
    sub_title = models.CharField(max_length=255) 
    qr_title = models.CharField(max_length=100)  
    qr_image = models.ImageField(upload_to='home/components/app/',null=True,blank=True)
    google_play_icon = models.ImageField(upload_to='home/components/app/',null=True,blank=True)
    google_play_url = models.TextField(null=True) 
    apple_store_icon = models.ImageField(upload_to='home/components/app/',null=True,blank=True)
    apple_store_url = models.TextField(null=True) 
    app_photo = models.ImageField(upload_to='home/components/app/')
    show_at_home = models.BooleanField(default=True) 
    
   

    def __str__(self):
        return f"Step {self.title}: {self.sub_title}"


class FAQSection(models.Model):
    title = models.CharField(max_length=100)
    sub_title = models.CharField(max_length=255) 
    main_image = models.ImageField(upload_to='home/components/faq/',null=True,blank=True)
    show_at_home = models.BooleanField(default=True) 
    
    def __str__(self):
        return f"Faq {self.title}"
    

class Question(models.Model):
    faq_section = models.ForeignKey(FAQSection,on_delete=models.CASCADE,related_name='questions')
    order = models.PositiveIntegerField()  
    question = models.CharField(max_length=100)  
    answer = models.TextField() 
    show_at_home = models.BooleanField(default=True) 
    
    class Meta:
        ordering = ['order'] 

    def __str__(self):
        return f"Step {self.order}: {self.question}"
    def save(self, *args, **kwargs):
        if not self.order: 
            max_order = Question.objects.filter(faq_section=self.faq_section).aggregate(models.Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)


class TestimonialSection(models.Model):
    title = models.CharField(max_length=100)  
    sub_title = models.TextField() 
    status = models.BooleanField(default=True)
    def __str__(self):
        return f"testimonial {self.title}"
    
        
class Testimonial(models.Model):
    testimonial = models.ForeignKey(TestimonialSection,on_delete=models.CASCADE,related_name="testimonials")
    main_image = models.ImageField(upload_to='home/components/testimonial/',null=True,blank=True)
    review = models.TextField() 
    order = models.PositiveIntegerField()  
    name = models.CharField(max_length=100)  
    country = models.CharField(max_length=100)  
    show_at_home = models.BooleanField(default=True)
    def __str__(self):
        return f"name {self.name}"
    
    class Meta:
        ordering = ['order'] 

    def save(self, *args, **kwargs):
        if not self.order: 
            max_order = Testimonial.objects.filter(testimonial=self.testimonial).aggregate(models.Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)
        

class PartnersSection(models.Model):
    pertner_image =  models.ImageField(upload_to='home/components/partners/',null=True,blank=True)
    show_at_home = models.BooleanField(default=True)
    def __str__(self):
        return f"parteners {self.pertner_image}"        