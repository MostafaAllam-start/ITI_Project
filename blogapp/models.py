from django.db import models
from django.conf import settings
from  django.utils import timezone
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from taggit.managers import TaggableManager


# Create your models here.
class PublishedManager(models.Manager):

    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')

class Post(models.Model):
    STATUES_CHOICES = (('draft','Draft'),('published','Published'))
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,unique_for_date='publish')
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='blog_posts')
    body = models.TextField()
    picture  = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,choices=STATUES_CHOICES,default='draft')
    published = PublishedManager()
    objects = models.Manager() # The default manager.
    tags = TaggableManager()

    def get_absolute_url(self):
        return reverse('blogapp:post_detail',args=[self.publish.year,self.publish.month,self.publish.day,self.slug])

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args,**kwargs)

    def number_of_likes(self):
        return self.likes.count()


    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title



class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    name = models.CharField(max_length=32)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f'Comment created by {self.name} on {self.post}'


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="user_profile", on_delete=models.CASCADE)
    restrict = models.BooleanField(blank=True, null=True, default=False)
    date_of_birth = models.DateField(blank=True,null = True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/',blank=True)
    description = models.TextField(null=True)
    def __str__(self):
        return f'Profile for user {self.user.username}'

class Blocked_words(models.Model):
    bow = models.TextField()

    def __str__(self):
       return self.bow