from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# custom manager for published posts
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

# Post model
class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')

    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)

    objects = models.Manager()      # if you want default manager with custom one: you should declare default one like this
    published = PublishedManager()

    class Meta:
        # set default order
        ordering = ['-publish']
        # set indexing
        indexes = [
        models.Index(fields=['-publish']),
        ]

  # set how the post be represented 
    def __str__(self):
        return self.title
  
