from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse

from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التعديل")
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الحذف")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_created",
        verbose_name=_("المنشى"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_updated",
        verbose_name=_("المعدل"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    slug = models.SlugField(
        unique=True,
        max_length=255,
        verbose_name=_("Slug"),
        blank=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super(BaseModel, self).save(*args, **kwargs)

    def generate_unique_slug(self):
        base_slug = slugify(self.name) if hasattr(self, 'name') and self.name else slugify(str(self.id) if self.id else str(self))
        slug = base_slug
        num = 1

        model_class = self.__class__
        while model_class.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{num}'
            num += 1

        return slug

    def get_absolute_url(self):
        return reverse(f"{self.__class__.__name__.lower()}_detail", kwargs={"slug": self.slug})


# نموذج المستشفيات
class Hospital(BaseModel):
    name = models.CharField(max_length=100)
    hospital_manager_id = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


# تفاصيل المستشفى
class HospitalDetail(BaseModel):
    hospital = models.OneToOneField(Hospital, on_delete=models.CASCADE, related_name='details')
    description = models.TextField()
    specialty = models.ForeignKey('doctors.Specialty', on_delete=models.CASCADE)
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE,related_name='doctors')
    photo = models.ImageField(upload_to='hospital_images/', blank=True, null=True)  
    sub_title = models.CharField(max_length=255)
    about = models.TextField()
    status = models.BooleanField(default=True)
    show_at_home = models.BooleanField(default=True)

    def __str__(self):
        return f"Details for {self.hospital.name}"

# أرقام الهواتف
class PhoneNumber(BaseModel):
    name = models.CharField(max_length=14)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='phone_numbers')
    
    def __str__(self):
        return f"{self.name} - {self.hospital.name}"


