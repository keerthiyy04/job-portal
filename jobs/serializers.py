from rest_framework import serializers
from .models import Job, Application, Notification, AdminLog
from django.contrib.auth import get_user_model

User = get_user_model()

# =========================================================
# JOB SERIALIZER
# =========================================================
class JobSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company",
            "stream",
            "description",
            "place",
            "salary",
            "job_type",
            "skills",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_skills(self, obj):
        if not obj.skills:
            return []
        if isinstance(obj.skills, list):
            return obj.skills
        if isinstance(obj.skills, str):
            return [s.strip() for s in obj.skills.split(",")]
        return []

# =========================================================
# MINI JOB SERIALIZER (USED INSIDE APPLICATION)
# =========================================================
class JobMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company",
            "place",
            "stream",
        ]

# =========================================================
# APPLICATION SERIALIZER
# =========================================================
class ApplicationSerializer(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all(), write_only=True)
    job_details = JobMiniSerializer(source="job", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    company = serializers.CharField(source="job.company", read_only=True)
    place = serializers.CharField(source="job.place", read_only=True)
    resume_url = serializers.SerializerMethodField()  # Full URL for browser/admin

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "job_details",
            "job_title",
            "company",
            "place",
            "name",
            "email",
            "phone",
            "resume",
            "resume_url",
            "cover_letter",
            "status",
            "admin_message",
            "applied_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "admin_message",
            "applied_at",
            "updated_at",
        ]

    def get_resume_url(self, obj):
        """Return full URL so resumes open in browser or download directly."""
        if not obj.resume:
            return None
        request = self.context.get("request")
        try:
            if request:
                return request.build_absolute_uri(obj.resume.url)
            return obj.resume.url
        except Exception:
            return None

# =========================================================
# ADMIN UPDATE APPLICATION
# =========================================================
class AdminUpdateApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["status", "admin_message"]

    def validate_status(self, value):
        valid_status = ["pending", "accepted", "rejected"]
        if value not in valid_status:
            raise serializers.ValidationError(f"Status must be one of {valid_status}")
        return value

# =========================================================
# NOTIFICATION SERIALIZERS
# =========================================================
class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "recipient", "message", "read", "timestamp"]
        read_only_fields = ["id", "recipient", "timestamp"]

# =========================================================
# CLIENT NOTIFICATION SERIALIZER
# =========================================================
class ClientNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "message", "read", "timestamp"]
        read_only_fields = ["id", "message", "timestamp"]

# =========================================================
# ADMIN LOG SERIALIZER
# =========================================================
class AdminLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminLog
        fields = ["id", "action", "created_at"]
        read_only_fields = ["id", "created_at"]