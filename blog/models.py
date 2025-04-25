from django.db import models
from doctors.models import BaseModel
from django.urls import reverse
from django.utils.text import slugify
from doctors_appointment import settings
from hospitals.models import Hospital


def author_directory_path(instance, filename):
    return f'blog/{instance.author.name}/{filename}'


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم التصنيف")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="الاسم في الرابط")
    status = models.BooleanField(default=False, verbose_name="الحالة")

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('home:blog:category_detail', args=[self.slug])


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="اسم الوسم")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="الاسم في الرابط")
    status = models.BooleanField(default=False, verbose_name="الحالة")

    class Meta:
        verbose_name = "وسم"
        verbose_name_plural = "الوسوم"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('home:blog:tag_detail', args=[self.slug])


class Post(BaseModel):
    title = models.CharField(max_length=200, verbose_name="عنوان المقال")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="الاسم في الرابط")
    content = models.TextField(verbose_name="المحتوى")
    image = models.ImageField(upload_to=author_directory_path, blank=True, null=True, verbose_name="الصورة")
    author = models.ForeignKey(Hospital, on_delete=models.CASCADE, verbose_name="الكاتب")
    categories = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="posts", verbose_name="التصنيف")
    tags = models.ManyToManyField('Tag', related_name="posts", verbose_name="الوسوم")
    status = models.BooleanField(default=False, verbose_name="الحالة")

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "مقال"
        verbose_name_plural = "المقالات"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super(Post, self).save(*args, **kwargs)

    def generate_unique_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        num = 1

        while Post.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{num}'
            num += 1

        return slug

    def get_absolute_url(self):
        return reverse('home:blog:post_detail', args=[self.slug])


class Comment(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="المقال")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_comments", verbose_name="المستخدم")
    content = models.TextField(verbose_name="المحتوى")
    status = models.BooleanField(default=False, verbose_name="الحالة")

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "تعليق"
        verbose_name_plural = "التعليقات"

    def __str__(self):
        return f"تعليق بواسطة {self.user.username} على {self.post.title}"
