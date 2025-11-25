from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings


# ------------------------------
# Custom User Model
# ------------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    # Override related names to avoid conflicts
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set_permissions',
        blank=True,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


# ------------------------------
# Barangay Area
# ------------------------------
class Area(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    AREA_CHOICES = [
        ('Naval', 'Naval'),
        ('Caibiran', 'Caibiran'),
        ('Cabucgayan', 'Cabucgayan'),
        ('Biliran', 'Biliran'),
        ('Almeria', 'Almeria'),
        ('Culaba', 'Culaba'),
        ('Kawayan', 'Kawayan'),
        ('Maripipi', 'Maripipi'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    area = models.CharField(max_length=100, choices=AREA_CHOICES)
    
    # --- EXISTING FIELD ---
    barangay = models.CharField(max_length=255, null=True, blank=True)
    
    # --- NEW FIELDS ---
    purok = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(upload_to='complaint_photos/', null=True, blank=True)

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pending'  # IMPORTANT: Use capitalized default
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints'
    )
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
# ------------------------------
# Complaint Photos
# ------------------------------
class ComplaintPhoto(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='complaint_photos/')

    def __str__(self):
        return f"Photo for {self.complaint.title}"


# ------------------------------
# Announcement
# ------------------------------
class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('maintenance', 'Maintenance'),
        ('emergency', 'Emergency'),
        ('update', 'Update'),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    is_pinned = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ------------------------------
# Bailing Schedule
# ------------------------------
class BailingSchedule(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
    ]

    location = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    truck_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

    def __str__(self):
        return f"{self.location} - {self.date} {self.time}"


# ------------------------------
# Activity Log
# ------------------------------
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        user_display = self.user.username if self.user else 'System'
        return f"{user_display} - {self.action} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


# ------------------------------
# Feedback (merged version)
# ------------------------------
class Feedback(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]
    STATUS_CHOICES = [
        ('Reviewed', 'Reviewed'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # custom User
    complaint = models.ForeignKey(Complaint, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    rating = models.IntegerField(default=1)
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, default='neutral')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Reviewed')
    issue_area = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.rating}⭐)"

    @property
    def sentiment_label(self):
        if self.rating >= 4:
            return "positive"
        elif self.rating == 3:
            return "neutral"
        else:
            return "negative"


# ------------------------------
# Water Bill
# ------------------------------
class WaterBill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    status = models.CharField(max_length=10, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')])
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    reference_no = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.month} {self.year}"


# ------------------------------
# Notification
# ------------------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}"

class Municipality(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Report(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='reports/', null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    address = models.CharField(max_length=255, null=True, blank=True)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    issue_type = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    # ADD THIS ↓↓↓
    barangay = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

