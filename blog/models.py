from django.db import models
from doctors.models import BaseModel
from django.urls import reverse
from django.utils.text import slugify
from doctors_appointment import settings
from hospitals.models import Hospital

# Create your models here.



def author_directory_path(instance, filename):
    """
    Generate a path for uploaded files based on the author's username.
    E.g., media/blog/author_username/filename
    """
    return f'blog/{instance.author.name}/{filename}'



class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('home:blog:category_detail', args=[self.slug])

class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('home:blog:tag_detail', args=[self.slug])

class Post(BaseModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    image = models.ImageField(upload_to=author_directory_path, blank=True, null=True)
    author = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    categories = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="posts")
    tags = models.ManyToManyField('Tag', related_name="posts")
    status = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_at',)
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
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_comments")
    content = models.TextField()
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
    class Meta:
        ordering = ('-created_at',)

   
