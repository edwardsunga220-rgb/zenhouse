from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.urls import reverse
from django.core.validators import MinValueValidator, FileExtensionValidator, MinLengthValidator
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class ContactMessage(models.Model):
    """
    A message sent from the contact page.
    Optionally links to a MainMap (when user inquires from a specific project).
    """
    main_map = models.ForeignKey(
        'MainMap',  # string avoids import cycle
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='contact_messages'
    )
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField(validators=[MinLengthValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        subj = self.subject or "No subject"
        return f"{self.name} — {subj}"

class MainMap(models.Model):
    # ---- Categories ----
    CATEGORY_APARTMENTS = 'apartments'
    CATEGORY_RESIDENTIAL = 'residential'
    CATEGORY_VILLA = 'villa'
    CATEGORY_HOTELS = 'hotels'
    CATEGORY_OFFICES = 'offices'
    CATEGORY_BEACH_HOUSE = 'beach_house'
    CATEGORY_COMMERCIAL = 'commercial'
    CATEGORY_OTHER = 'other'

    CATEGORY_CHOICES = [
        (CATEGORY_APARTMENTS, 'Apartments'),
        (CATEGORY_RESIDENTIAL, 'Residential'),
        (CATEGORY_VILLA, 'Villa'),
        (CATEGORY_HOTELS, 'Hotels'),
        (CATEGORY_OFFICES, 'Offices'),
        (CATEGORY_BEACH_HOUSE, 'Beach House'),
        (CATEGORY_COMMERCIAL, 'Commercial'),
        (CATEGORY_OTHER, 'Other'),
    ]

    # ---- Style ----
    STYLE_CHOICES = [
        ('modern', 'Modern'),
        ('contemporary', 'Contemporary'),
        ('bungalow', 'Bungalow'),
        ('colonial', 'Colonial'),
        ('cottage', 'Cottage'),
        ('other', 'Other'),  # allow user to type their own style
    ]

    title = models.CharField(max_length=200)
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Enter unique property code (letters, numbers, or symbols)"
    )
    detail = models.TextField(blank=True)
    image = models.ImageField(upload_to='maps/main/')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    # Price
    price = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Enter property price"
    )

    # Style
    style = models.CharField(
        max_length=50,
        choices=STYLE_CHOICES,
        default='modern'
    )
    custom_style = models.CharField(
        max_length=100,
        blank=True,
        help_text="Enter a custom style if not in the list"
    )

    number_of_floors = models.PositiveSmallIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1)],
        help_text="Optional: Number of floors"
    )

    number_of_bathrooms = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Enter number of bathrooms (min 1)"
    )
    number_of_bedrooms = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Enter number of bedrooms (min 1)"
    )

    square_meters = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Enter the size in square meters"
    )

    design_file = models.FileField(
        upload_to='maps/files/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'cad', 'dwg'])],
        help_text="Upload design file (PDF or CAD)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.code})"

    def get_style_display_value(self):
        """Return custom style if 'Other' is selected"""
        return self.custom_style if self.style == 'other' and self.custom_style else self.get_style_display()


class MainMapDetail(models.Model):
    main_map = models.ForeignKey(MainMap, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=200, blank=True, null=True)
    detail = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='maps/details/')

    # Design file upload for details
    design_file = models.FileField(
        upload_to='maps/details/files/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'cad', 'dwg'])],
        help_text="Upload design file (PDF or CAD)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        if self.title:
            return f"{self.main_map.title} · {self.title}"
        return f"{self.main_map.title} · Detail {self.id}"

class CustomPlanRequest(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    requirements = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"

class Article(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    hero = models.ImageField(upload_to="articles/hero/", blank=True, null=True)
    file = models.FileField(upload_to="articles/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="uploaded_articles"
    )
    views = models.PositiveIntegerField(default=0)  # Track views

    def __str__(self):
        return self.title
    
    @property
    def is_image(self):
        if not self.file:
            return False
        return self.file.name.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))
    
    @property
    def excerpt(self):
        if self.description:
            return self.description[:200]  # first 200 characters
        return ""
    
    from django.db import models

# In your models.py
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    page = models.CharField(max_length=50, blank=True, help_text="Page where form was submitted")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Add this field
    is_processed = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.name} - {self.subject}"