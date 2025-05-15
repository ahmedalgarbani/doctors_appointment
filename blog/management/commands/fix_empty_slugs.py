from django.core.management.base import BaseCommand
from blog.models import Post

class Command(BaseCommand):
    help = 'Fix posts with empty slugs'

    def handle(self, *args, **options):
        posts_with_empty_slugs = Post.objects.filter(slug='')
        count = posts_with_empty_slugs.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No posts with empty slugs found.'))
            return
            
        self.stdout.write(f'Found {count} posts with empty slugs. Fixing...')
        
        for post in posts_with_empty_slugs:
            post.slug = post.generate_unique_slug()
            post.save()
            self.stdout.write(f'Fixed post ID {post.id}: "{post.title}" - new slug: {post.slug}')
            
        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {count} posts.'))
