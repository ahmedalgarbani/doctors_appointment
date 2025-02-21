from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404,redirect
from .models import Post, Category, Tag
from .forms import CommentForm

def post_list(request):
    posts = Post.objects.filter(status=True)  
    tags = Tag.objects.filter(status=True) 
    categories = Category.objects.filter(status=True)  
    paginator = Paginator(posts, 10)  
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number)  

    ctx = {
        'page_obj': page_obj, 
        'tags': tags,
        'categories': categories,
    }
    return render(request, 'frontend/home/pages/allblog.html', ctx)

def post_detail(request,slug):
    post = get_object_or_404(Post, slug=slug) 
    tags = Tag.objects.filter(status=True) 
    posts = Post.objects.filter(status=True)  
    categories = Category.objects.filter(status=True)
    #----- create comment and redirect to post details ---
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post 
            comment.user = request.user  
            comment.save()
            return redirect('home:blog:post_detail', slug=slug)  
    else:
        form = CommentForm()
    ctx = {
        'post':post,
        'posts':posts,
        'categories':categories,
        'tags':tags,
    }   
    return render(request, 'frontend/home/pages/blog_details.html', ctx)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = category.posts.filter(status=True) 
    tags = Tag.objects.filter(status=True) 
    categories = Category.objects.filter(status=True)  


    paginator = Paginator(posts, 10)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number) 

    ctx = {
        'page_obj': page_obj, 
        'tags': tags,
        'categories': categories,
    }
    return render(request, 'frontend/home/pages/allblog.html', ctx)


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = tag.posts.filter(status=True)  
    tags = Tag.objects.filter(status=True)  
    categories = Category.objects.filter(status=True) 

    paginator = Paginator(posts, 10) 
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number)  

    ctx = {
        'page_obj': page_obj,
        'tags': tags,
        'categories': categories,
    }
    return render(request, 'frontend/home/pages/allblog.html', ctx)
