from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse
from users.models import CustomUser
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


    class Meta:
        abstract = True

class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("اسم المدينة"))
    slug = models.SlugField(unique=True, blank=True, verbose_name=_("الرمز المميز"))
    status = models.BooleanField(default=True, verbose_name=_("الحالة"))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("مدينة")
        verbose_name_plural = _("مدينة")


class Hospital(BaseModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='hospital',
        verbose_name=_("حساب المستخدم"),
        limit_choices_to={'user_type': 'hospital_manager'},
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        related_name='hospitals',
        verbose_name=_("المدينة")
    )
    name = models.CharField(max_length=100, verbose_name=_("اسم المستشفى"))
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name=_("الرابط المختصر")
    )
    logo = models.ImageField(
        upload_to='hospital_logos/',
        null=True,
        blank=True,
        verbose_name=_("شعار المستشفى"),
        help_text=_(" .رفع شعار المستشفى")
    )
    description = models.TextField(
        null=True, blank=True, verbose_name=_("الوصف")
    )
    sub_title = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("العنوان الفرعي")
    )
    about = models.TextField(null=True, blank=True, verbose_name=_("حول"))
    status = models.BooleanField(default=True, verbose_name=_("الحالة"))
    show_at_home = models.BooleanField(
        default=True, verbose_name=_("إظهار في الصفحة الرئيسية")
    )
    commercial_record = models.FileField(
        upload_to='hospital_documents/',
        null=True,
        blank=True,
        verbose_name=_("السجل التجاري"),
        help_text=_("يرجى رفع نسخة من السجل التجاري للمستشفى"),
    )
    medical_license = models.FileField(
        upload_to='hospital_documents/',
        null=True,
        blank=True,
        verbose_name=_("الترخيص الطبي"),
        help_text=_("يرجى رفع نسخة من الترخيص الطبي للمستشفى"),
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('home:hospitals:hospital_detail', args=[self.slug])

    class Meta:
        verbose_name = _("مستشفى")
        verbose_name_plural = _("مستشفيات")


class PhoneNumber(BaseModel):
    number = models.CharField(max_length=14,verbose_name=_("رقم الهاتف"))
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='phone_numbers',verbose_name=_("المستشفى"))
    phone_type = models.CharField(
        max_length=50,
        choices=[
            ('landline', _("هاتف أرضي")),
            ('mobile', _("هاتف محمول"))
        ],
        default='mobile',
        verbose_name=_("نوع الهاتف")
    )

    def __str__(self):
        return f"{self.number} ({self.phone_type}) - {self.hospital.name}"

    class Meta:
        verbose_name = _("رقم هاتف")
        verbose_name_plural = _("أرقام الهواتف")


class HospitalAccountRequest(BaseModel):
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('approved', _('تمت الموافقة')),
        ('rejected', _('مرفوض')),
    ]

    hospital_name = models.CharField(
        max_length=100,
        verbose_name=_("اسم المستشفى")
    )
    manager_full_name = models.CharField(
        max_length=255,
        verbose_name=_("اسم مدير المستشفى")
    )
    logo = models.ImageField(
        upload_to='hospital_logos/',
        null=True,
        blank=True,
        verbose_name=_("شعار المستشفى"),
        help_text=_(" .رفع شعار المستشفى")
    )
    manager_email = models.EmailField(
        verbose_name=_("البريد الإلكتروني للمدير")
    )
    manager_phone = models.CharField(
        max_length=20,
        verbose_name=_("رقم هاتف المدير")
    )
    manager_password = models.CharField(
        max_length=128,
        verbose_name=_("كلمة المرور"),
        help_text=_("كلمة المرور التي سيتم استخدامها لحساب مدير المستشفى")
    )
    hospital_location = models.CharField(
        max_length=255,
        verbose_name=_("موقع المستشفى")
    )
    commercial_record = models.FileField(
        upload_to='hospital_documents/',
        verbose_name=_("السجل التجاري"),
        help_text=_("يرجى رفع نسخة من السجل التجاري للمستشفى")
    )
    medical_license = models.FileField(
        upload_to='hospital_documents/',
        verbose_name=_("الترخيص الطبي"),
        help_text=_("يرجى رفع نسخة من الترخيص الطبي للمستشفى")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("حالة الطلب")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("ملاحظات"),
        help_text=_("ملاحظات إضافية حول الطلب")
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_hospital_requests',
        verbose_name=_("تمت المراجعة بواسطة")
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ المراجعة")
    )

    class Meta:
        verbose_name = _("طلب فتح حساب مستشفى")
        verbose_name_plural = _("طلبات فتح حساب مستشفى")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.hospital_name} - {self.get_status_display()}"

    def approve_request(self, reviewed_by):
        from django.utils import timezone

        # تحديث حالة الطلب
        self.status = 'approved'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()

        # حفظ الكائن لتفعيل طريقة save التي ستقوم بإنشاء المستخدم والمستشفى
        self.save()

    def reject_request(self, reviewed_by, notes=None):
        from django.utils import timezone
        self.status = 'rejected'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        if notes:
            self.notes = notes
        self.save()

    def save(self, *args, **kwargs):
        # التحقق من أن الحالة تغيرت إلى "تمت الموافقة"
        if self.pk and not hasattr(self, '_creating_user_and_hospital'):  # التحقق من أن الكائن موجود بالفعل ولم يتم استدعاؤه من داخل approve_request
            try:
                original = HospitalAccountRequest.objects.get(pk=self.pk)
                if original.status != 'approved' and self.status == 'approved' and self.reviewed_by:
                    # وضع علامة لتجنب الحلقة اللانهائية
                    self._creating_user_and_hospital = True

                    # إنشاء حساب مستخدم جديد لمدير المستشفى
                    from django.utils import timezone
                    from django.utils.text import slugify
                    from django.contrib.auth import get_user_model

                    User = get_user_model()

                    # التحقق من عدم وجود مستخدم بنفس البريد الإلكتروني
                    if not User.objects.filter(email=self.manager_email).exists():
                        # إنشاء حساب مستخدم جديد لمدير المستشفى
                        user = User.objects.create_user(
                            username=self.manager_email,  # استخدام البريد الإلكتروني كاسم مستخدم
                            email=self.manager_email,
                            first_name=self.manager_full_name.split(' ')[0],
                            last_name=' '.join(self.manager_full_name.split(' ')[1:]),
                            user_type='hospital_manager',
                            mobile_number=self.manager_phone,
                        )
                        user.set_password(self.manager_password)
                        user.save()

                        # إنشاء سجل المستشفى
                        hospital_slug = slugify(self.hospital_name)
                        # التحقق من وجود slug مشابه وإضافة رقم تسلسلي إذا لزم الأمر
                        original_slug = hospital_slug
                        counter = 1
                        while Hospital.objects.filter(slug=hospital_slug).exists():
                            hospital_slug = f"{original_slug}-{counter}"
                            counter += 1

                        # إنشاء سجل المستشفى
                        Hospital.objects.create(
                            user=user,  # ربط المستشفى بالمستخدم
                            name=self.hospital_name,
                            slug=hospital_slug,  # الرابط المختصر للمستشفى
                            logo=self.logo,
                            description=self.notes,
                            commercial_record=self.commercial_record,
                            medical_license=self.medical_license,
                            created_by=self.reviewed_by,
                            created_at=timezone.now()
                        )

                        # إرسال بريد إلكتروني بمعلومات تسجيل الدخول
                        subject = 'تمت الموافقة على طلب تسجيل المستشفى'
                        message = f'''مرحباً {self.manager_full_name}،
                        تمت الموافقة على طلب تسجيل المستشفى الخاص بكم. يمكنكم الآن تسجيل الدخول باستخدام المعلومات التالية:
                        اسم المستخدم: {user.username}
                        كلمة المرور: {self.manager_password}
                        يرجى تغيير كلمة المرور بعد تسجيل الدخول لأول مرة.
                        '''
                        try:
                            user.email_user(subject, message)
                        except Exception:
                            # لا نقوم بأي إجراء في حالة فشل إرسال البريد الإلكتروني
                            pass
            except Exception:
                pass  # في حالة حدوث أي خطأ، نستمر في حفظ الكائن بشكل عادي
            finally:
                if hasattr(self, '_creating_user_and_hospital'):
                    delattr(self, '_creating_user_and_hospital')

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("طلب فتح حساب مستشفى")
        verbose_name_plural = _("طلبات فتح حساب مستشفى")


class HospitalUpdateRequest(BaseModel):
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('approved', _('تمت الموافقة')),
        ('rejected', _('مرفوض')),
    ]
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, verbose_name=_("المستشفى"))
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("اسم المستشفى"))
    logo = models.ImageField(
        upload_to='hospital_logos/',
        null=True,
        blank=True,
        verbose_name=_("شعار المستشفى"),
    )
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("الموقع"))
    description = models.TextField(null=True, blank=True, verbose_name=_("الوصف"))
    specialty = models.ForeignKey('doctors.Specialty', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("التخصص"))
    photo = models.ImageField(upload_to='hospital_images/', blank=True, null=True, verbose_name=_("الصورة"))
    sub_title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("العنوان الفرعي"))
    about = models.TextField(null=True, blank=True, verbose_name=_("حول"))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("حالة الطلب")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("ملاحظات"),
        help_text=_("ملاحظات إضافية حول الطلب")
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_hospital_update_requests',
        verbose_name=_("تمت المراجعة بواسطة")
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ المراجعة")
    )

    class Meta:
        verbose_name = _("طلب تعديل بيانات مستشفى")
        verbose_name_plural = _("طلبات تعديل بيانات مستشفى")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.hospital.name} - {self.get_status_display()}"

    def approve_request(self, reviewed_by):
      from django.utils import timezone
      self.status = 'approved'
      self.reviewed_by = reviewed_by
      self.reviewed_at = timezone.now()

      # تحديث بيانات المستشفى
      hospital = self.hospital
      if self.name:
        hospital.name = self.name
      if self.location:
        hospital.location = self.location
      if self.description:
        hospital.description = self.description

      if self.photo:
        hospital.photo = self.photo
      if self.sub_title:
        hospital.sub_title = self.sub_title
      if self.about:
        hospital.about = self.about
      hospital.save()

      self.save()

    def reject_request(self, reviewed_by, notes=None):
        from django.utils import timezone
        self.status = 'rejected'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        if notes:
            self.notes = notes
        self.save()
