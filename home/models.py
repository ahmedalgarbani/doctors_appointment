from django.db import models
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _
from hospitals.models import BaseModel

class HomeBanner(models.Model):
    title = models.CharField(_("العنوان"), max_length=255)
    subtitle = models.TextField(_("العنوان الفرعي"), blank=True, null=True)
    header_icon = models.ImageField(_("أيقونة الهيدر"), upload_to='home/components/homebanner/icons/', blank=True, null=True)
    main_image = models.ImageField(_("الصورة الرئيسية"), upload_to='home/components/homebanner/', blank=True, null=True)
    sub_image1 = models.ImageField(_("الصورة الفرعية 1"), upload_to='home/components/homebanner/', blank=True, null=True)
    sub_image2 = models.ImageField(_("الصورة الفرعية 2"), upload_to='home/components/homebanner/', blank=True, null=True)
    sub_image3 = models.ImageField(_("الصورة الفرعية 3"), upload_to='home/components/homebanner/', blank=True, null=True)

    class Meta:
        verbose_name = _("بانر الصفحة الرئيسية")
        verbose_name_plural = _("بنرات الصفحة الرئيسية")

    def __str__(self):
        return self.title


class WorkSection(models.Model):
    title = models.CharField(_("العنوان"), max_length=150)
    sub_title = models.CharField(_("العنوان الفرعي"), max_length=255)
    main_image = models.ImageField(_("الصورة الرئيسية"), upload_to='home/components/work/')

    class Meta:
        verbose_name = _("قسم كيف نعمل")
        verbose_name_plural = _("أقسام كيف نعمل")

    def __str__(self):
        return f"{self.title}: {self.sub_title}"


class WorkStep(models.Model):
    work_section = models.ForeignKey(WorkSection, on_delete=models.CASCADE, related_name='steps', verbose_name=_("قسم العمل"))
    order = models.PositiveIntegerField(_("الترتيب"))
    title = models.CharField(_("العنوان"), max_length=100)
    description = models.TextField(_("الوصف"))
    icon = models.ImageField(_("الأيقونة"), upload_to='home/components/work/icons/')
    show_at_home = models.BooleanField(_("إظهار في الصفحة الرئيسية"), default=True)

    class Meta:
        ordering = ['order']
        verbose_name = _("خطوة عمل")
        verbose_name_plural = _("خطوات العمل")

    def __str__(self):
        return f"Step {self.order}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.order:
            max_order = WorkStep.objects.filter(work_section=self.work_section).aggregate(models.Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)


class AppSection(models.Model):
    title = models.CharField(_("العنوان"), max_length=100)
    sub_title = models.CharField(_("العنوان الفرعي"), max_length=255)
    qr_title = models.CharField(_("عنوان رمز QR"), max_length=100)
    qr_image = models.ImageField(_("صورة رمز QR"), upload_to='home/components/app/', null=True, blank=True)
    google_play_icon = models.ImageField(_("أيقونة Google Play"), upload_to='home/components/app/', null=True, blank=True)
    google_play_url = models.TextField(_("رابط Google Play"), null=True)
    apple_store_icon = models.ImageField(_("أيقونة Apple Store"), upload_to='home/components/app/', null=True, blank=True)
    apple_store_url = models.TextField(_("رابط Apple Store"), null=True)
    app_photo = models.ImageField(_("صورة التطبيق"), upload_to='home/components/app/')
    show_at_home = models.BooleanField(_("إظهار في الصفحة الرئيسية"), default=True)

    class Meta:
        verbose_name = _("قسم التطبيق")
        verbose_name_plural = _("أقسام التطبيق")

    def __str__(self):
        return f"{self.title}: {self.sub_title}"


class FAQSection(models.Model):
    title = models.CharField(_("العنوان"), max_length=100)
    sub_title = models.CharField(_("العنوان الفرعي"), max_length=255)
    main_image = models.ImageField(_("الصورة الرئيسية"), upload_to='home/components/faq/', null=True, blank=True)
    show_at_home = models.BooleanField(_("إظهار في الصفحة الرئيسية"), default=True)

    class Meta:
        verbose_name = _("قسم الأسئلة الشائعة")
        verbose_name_plural = _("أقسام الأسئلة الشائعة")

    def __str__(self):
        return f"Faq {self.title}"


class Question(models.Model):
    faq_section = models.ForeignKey(FAQSection, on_delete=models.CASCADE, related_name='questions', verbose_name=_("قسم الأسئلة"))
    order = models.PositiveIntegerField(_("الترتيب"))
    question = models.CharField(_("السؤال"), max_length=100)
    answer = models.TextField(_("الإجابة"))
    show_at_home = models.BooleanField(_("إظهار في الصفحة الرئيسية"), default=True)

    class Meta:
        ordering = ['order']
        verbose_name = _("سؤال")
        verbose_name_plural = _("الأسئلة")

    def __str__(self):
        return f"Step {self.order}: {self.question}"

    def save(self, *args, **kwargs):
        if not self.order:
            max_order = Question.objects.filter(faq_section=self.faq_section).aggregate(models.Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)


class TestimonialSection(models.Model):
    title = models.CharField(_("العنوان"), max_length=100)
    sub_title = models.TextField(_("العنوان الفرعي"))
    status = models.BooleanField(_("الحالة"), default=True)

    class Meta:
        verbose_name = _("قسم التوصيات")
        verbose_name_plural = _("أقسام التوصيات")

    def __str__(self):
        return f"testimonial {self.title}"


class Testimonial(models.Model):
    testimonial = models.ForeignKey(TestimonialSection, on_delete=models.CASCADE, related_name="testimonials", verbose_name=_("القسم"))
    main_image = models.ImageField(_("الصورة"), upload_to='home/components/testimonial/', null=True, blank=True)
    review = models.TextField(_("التوصية"))
    order = models.PositiveIntegerField(_("الترتيب"))
    name = models.CharField(_("الاسم"), max_length=100)
    country = models.CharField(_("الدولة"), max_length=100)
    show_at_home = models.BooleanField(_("إظهار في الصفحة الرئيسية"), default=True)

    class Meta:
        ordering = ['order']
        verbose_name = _("توصية")
        verbose_name_plural = _("توصيات")

    def __str__(self):
        return f"name {self.name}"

    def save(self, *args, **kwargs):
        if not self.order:
            max_order = Testimonial.objects.filter(testimonial=self.testimonial).aggregate(models.Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)


class PartnersSection(models.Model):
    pertner_image = models.ImageField(_("صورة الشريك"), upload_to='home/components/partners/', null=True, blank=True)
    show_at_home = models.BooleanField(_("إظهار في الصفحة الرئيسية"), default=True)

    class Meta:
        verbose_name = _("شريك")
        verbose_name_plural = _("الشركاء")

    def __str__(self):
        return f"parteners {self.pertner_image}"


class SocialMediaLink(models.Model):
    name = models.CharField(_("الاسم"), max_length=100)
    link = models.CharField(_("الرابط"), max_length=255)
    icon = models.CharField(_("الأيقونة"), max_length=100)
    status = models.BooleanField(_("الحالة"), default=True)

    class Meta:
        verbose_name = _("رابط تواصل اجتماعي")
        verbose_name_plural = _("روابط التواصل الاجتماعي")

    def __str__(self):
        return f"socialmedia {self.name}"


class PrivacyPolicy(BaseModel):
    name = models.CharField(_("الاسم"), default='privacypolicy', max_length=150)
    content = RichTextField(_("المحتوى"))

    class Meta:
        verbose_name = _("سياسة الخصوصية")
        verbose_name_plural = _("سياسات الخصوصية")

    def __str__(self):
        return f"privacy_policy {self.name}"


class TermsConditions(BaseModel):
    name = models.CharField(_("الاسم"), default='terms and conditions', max_length=150)
    content = RichTextField(_("المحتوى"))

    class Meta:
        verbose_name = _("الشروط والأحكام")
        verbose_name_plural = _("الشروط والأحكام")

    def __str__(self):
        return f"terms_conditions {self.name}"


class Setting(models.Model):
    STATUS_LEFT = 0
    STATUS_RIGHT = 1

    STATUS_CHOICES = [
        (STATUS_LEFT, _('يسار')),
        (STATUS_RIGHT, _('يمين')),
    ]

    site_name = models.CharField(_("اسم الموقع"), max_length=100)
    description = models.CharField(_("الوصف"), max_length=255)
    default_currency = models.CharField(_("العملة الافتراضية"), max_length=100)
    color = models.CharField(_("اللون الأساسي"), max_length=100)
    currency_icon = models.CharField(_("أيقونة العملة"), max_length=10)
    default_language = models.CharField(_("اللغة الافتراضية"), max_length=100)
    currency_Icon_position = models.IntegerField(_("مكان أيقونة العملة"), choices=STATUS_CHOICES, default=STATUS_LEFT)
    logo = models.ImageField(_("الشعار"), upload_to='home/components/setting/', null=True, blank=True)
    favicon = models.ImageField(_("أيقونة المتصفح"), upload_to='home/components/setting/', null=True, blank=True)
    footer_logo = models.ImageField(_("شعار الفوتر"), upload_to='home/components/setting/', null=True, blank=True)
    seo_title = models.CharField(_("عنوان SEO"), max_length=255)
    seo_description = models.TextField(_("وصف SEO"))
    seo_keywords = models.TextField(_("كلمات SEO المفتاحية"))

    class Meta:
        verbose_name = _("الإعدادات")
        verbose_name_plural = _("الإعدادات")

    def __str__(self):
        return f"setting {self.site_name}"
