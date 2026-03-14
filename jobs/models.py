from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


# ================== JOB MODEL ==================
class Job(models.Model):
    STREAM_CHOICES = [
        ("IT", "IT"),
        ("Marketing", "Marketing"),
        ("Finance", "Finance"),
        ("HR", "HR"),
        ("Other", "Other"),
    ]

    JOB_TYPE_CHOICES = [
        ("Full Time", "Full Time"),
        ("Part Time", "Part Time"),
        ("Internship", "Internship"),
        ("Contract", "Contract"),
        ("Other", "Other"),
    ]

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    stream = models.CharField(max_length=50, choices=STREAM_CHOICES)
    description = models.TextField()
    place = models.CharField(max_length=255, blank=True, null=True)
    salary = models.CharField(
        max_length=100, blank=True, null=True, help_text="Example: 3 LPA, 50k/month"
    )
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default="Full Time")
    skills = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.company}"


# ================== APPLICATION MODEL ==================
class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="applications")
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    resume = models.FileField(upload_to="resumes/")
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    admin_message = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.name} applied for {self.job.title}"


# ================== NOTIFICATION MODEL ==================
class Notification(models.Model):
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications", blank=True, null=True
    )  # Null = admin notification
    message = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Notification - {self.message[:40]}"


# ================== ADMIN LOG MODEL ==================
class AdminLog(models.Model):
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} - {self.created_at}"


# ================== SIGNALS ==================
@receiver(post_save, sender=Application)
def application_post_save(sender, instance, created, **kwargs):
    """
    Automatically create notifications and admin logs when:
    - A new application is submitted
    - Application status changes
    """

    # New application submission
    if created:
        # Admin notification
        Notification.objects.create(
            message=f"📩 New application from {instance.name} for {instance.job.title}",
            recipient=None  # Admin notification
        )
        AdminLog.objects.create(
            action=f"New application submitted by {instance.name} for {instance.job.title}"
        )

        # Client notification
        if instance.user:
            Notification.objects.create(
                message=f"✅ Your application for {instance.job.title} has been submitted",
                recipient=instance.user
            )

    # Status update
    else:
        # Only create notification if status actually changed
        if 'status' in instance.__dict__:
            if instance.user:
                Notification.objects.create(
                    message=f"📢 Your application for {instance.job.title} is now {instance.status.upper()}",
                    recipient=instance.user
                )
        AdminLog.objects.create(
            action=f"Application status updated to {instance.status.upper()} for {instance.name}"
        )