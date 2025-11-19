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


# ------------------- COURSE EDITION --------------------

class CourseEdition(models.Model):
    ONLINE = 'online'
    OFFLINE = 'offline'
    TYPE_CHOICES = [(ONLINE, 'Online'), (OFFLINE, 'Offline')]

    LEVEL_CHOICES = [("beginner", "Beginner"), ("intermediate", "Intermediate"), ("advanced", "Advanced")]

    course = models.ForeignKey(Course, related_name='editions', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, help_text='Ex. “1404 Winter”')
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    instructors = models.ManyToManyField(
        UserProfile,
        related_name="course_editions_taught",
        limit_choices_to={'is_instructor': True}
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default=ONLINE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True)

    capacity = models.PositiveIntegerField(null=True, blank=True)
    price = models.PositiveIntegerField(default=0)
    allow_group_purchase = models.BooleanField(default=False)

    # قوانین کسب‌وکار آنلاین/آفلاین
    enroll_open_from = models.DateField(null=True, blank=True)  # فقط آنلاین معنا دارد
    enroll_open_until = models.DateField(null=True, blank=True)  # فقط آنلاین معنا دارد
    access_duration_days = models.PositiveIntegerField(null=True, blank=True)  # آفلاین: مدت دسترسی

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'title')
        ordering = ['-start_date']

    def clean(self):
        # اعتبارسنجی بازه ثبت‌نام آنلاین
        if self.type == self.ONLINE:
            if self.enroll_open_until and self.start_date and self.enroll_open_until > self.start_date:
                raise ValidationError(
                    {"enroll_open_until": "Enroll until must be on or before start_date for online editions."})
        # اعتبارسنجی مدت دسترسی آفلاین
        if self.type == self.OFFLINE and not self.access_duration_days:
            raise ValidationError({"access_duration_days": "Offline editions must define access_duration_days."})

    def save(self, *args, **kwargs):
        if not self.slug:
            # اسلاگ ترکیبی تا طبیعی‌تر یکتا شود
            base = slugify(f"{self.course.slug}-{self.title}")[:255]
            self.slug = base
        super().save(*args, **kwargs)

    @property
    def seats_taken(self):
        return self.enrollments.filter(is_active=True).count()

    @property
    def available_seats(self):
        if self.capacity is None:
            return None
        return max(self.capacity - self.seats_taken, 0)

    def get_price(self, participants=1):
        if not self.allow_group_purchase or participants <= 1:
            return self.price
        tier = self.group_pricings.filter(min_participants__lte=participants).order_by("-min_participants").first()
        if tier:
            return tier.price_per_person
        return self.price

    def get_total_price(self, participants=1):
        return self.get_price(participants) * participants

    def __str__(self):
        return f"{self.course.title} — {self.title}"


# -------------------- GROUP PRICING --------------------

class GroupPricing(models.Model):
    edition = models.ForeignKey(CourseEdition, related_name="group_pricings", on_delete=models.CASCADE)
    min_participants = models.PositiveIntegerField()
    price_per_person = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.edition} — {self.min_participants}+ => {self.price_per_person}"


# -------------------- MODULE --------------------

class Module(models.Model):
    title = models.CharField(max_length=255)
    edition = models.ForeignKey(CourseEdition, related_name='modules', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('edition', 'order')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.order:
                last_order = Module.objects.select_for_update().filter(edition=self.edition).aggregate(
                    max_order=Max("order")
                )["max_order"] or 0
                self.order = last_order + 1
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.edition.course.title} - {self.title}"



