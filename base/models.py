from django.db import models
from base.UserManager import *
from django.utils.text import slugify
import uuid
# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    mobile_number = models.CharField(max_length=50 , blank=True, null=True, unique=True)   
    createdAt = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    




class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    publish_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True)
    featured_image = models.ImageField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-publish_date']
        
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
       
        if not self.slug:
            unique_slug = slugify(self.title) + '-' + str(uuid.uuid4())[:8]
            self.slug = unique_slug
        super(Blog, self).save(*args, **kwargs)



class Teams(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    image = models.ImageField(upload_to='teams/', blank=True, null=True)
    position = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name