from django.db import models
from django.db import models, transaction
from django.db.models import Max
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import mimetypes

from accounts.models import User, UserProfile


# -------------------- CATEGORY --------------------

class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent', 'order']),
        ]

    def clean(self):
        if self.parent_id and self.parent_id == self.id:
            raise ValidationError("Category cannot be parent of itself.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# -------------------- COURSE MEDIA --------------------

class CourseMedia(models.Model):
    TYPE_CHOICES = [
        ("COVER", "Cover"),
        ("BANNER", "Banner"),
        ("ICON", "Icon"),
        ("GALLERY", "Gallery"),
    ]
    image = models.ImageField(upload_to="courses/media/")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    alt_text = models.CharField(max_length=255)

    def __str__(self):
        return self.alt_text


# -------------------- COURSE --------------------

class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='courses')
    media = models.ManyToManyField(CourseMedia, blank=True)
    session_count = models.PositiveIntegerField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



