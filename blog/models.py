from django.db import models
from django.contrib.auth.models import User
from doctors.models import BaseModel
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User

# Create your models here.



def author_directory_path(instance, filename):
    """
    Generate a path for uploaded files based on the author's username.
    E.g., media/blog/author_username/filename
    """
    return f'blog/{instance.author.username}/{filename}'



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
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="posts")
    tags = models.ManyToManyField('Tag', related_name="posts")
    status = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_at',)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('home:blog:post_detail', args=[self.slug])

class Comment(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    content = models.TextField()
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
    class Meta:
        ordering = ('-created_at',)

   
