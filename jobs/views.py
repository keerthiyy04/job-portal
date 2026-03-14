from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from .models import Job, Application, Notification, AdminLog
from .serializers import (
    JobSerializer,
    ApplicationSerializer,
    AdminUpdateApplicationSerializer,
    NotificationSerializer,
    AdminLogSerializer
)

User = get_user_model()


# ================= CLIENT PROFILE =================
class ClientProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        full_name = user.get_full_name() or ""
        email = user.email or ""
        phone = getattr(user, "phone", "")
        profile_complete = bool(full_name and email)

        return Response({
            "fullName": full_name,
            "email": email,
            "phone": phone,
            "profile_complete": profile_complete
        })

    def post(self, request):
        user = request.user
        full_name = request.data.get("fullName")
        email = request.data.get("email")
        phone = request.data.get("phone")

        if full_name:
            names = full_name.split(" ", 1)
            user.first_name = names[0]
            if len(names) > 1:
                user.last_name = names[1]

        if email:
            user.email = email

        if hasattr(user, "phone"):
            user.phone = phone

        user.save()

        return Response({"message": "Profile updated successfully"})


# ================= ADMIN JOB MANAGEMENT =================
class AdminJobListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, id=None):

        if id:
            job = get_object_or_404(Job, id=id)
            serializer = JobSerializer(job)
            return Response(serializer.data)

        jobs = Job.objects.all().order_by("-created_at")
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            job = serializer.save()
            AdminLog.objects.create(action=f"Admin created job {job.title}")
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    def put(self, request, id=None):
        job = get_object_or_404(Job, id=id)
        serializer = JobSerializer(job, data=request.data)

        if serializer.is_valid():
            job = serializer.save()
            AdminLog.objects.create(action=f"Admin updated job {job.title}")
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, id=None):
        job = get_object_or_404(Job, id=id)
        AdminLog.objects.create(action=f"Admin deleted job {job.title}")
        job.delete()

        return Response({"message": "Job deleted"}, status=204)


# ================= CLIENT JOB LIST =================
class ClientJobListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id=None):

        if id:
            job = get_object_or_404(Job, id=id)
            serializer = JobSerializer(job)
            return Response(serializer.data)

        jobs = Job.objects.filter(is_active=True).order_by("-created_at")
        serializer = JobSerializer(jobs, many=True)

        return Response(serializer.data)


# ================= APPLY JOB =================
class ApplyJobAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):

        job = get_object_or_404(Job, id=job_id)
        user = request.user

        name = request.data.get("name") or user.get_full_name()
        email = request.data.get("email") or user.email
        phone = request.data.get("phone") or getattr(user, "phone", "")
        cover_letter = request.data.get("cover_letter") or ""
        resume = request.FILES.get("resume")

        if not resume:
            return Response({"error": "Resume file is required"}, status=400)

        if Application.objects.filter(job=job, email=email).exists():
            return Response({"error": "You already applied for this job"}, status=400)

        application = Application.objects.create(
            job=job,
            user=user,
            name=name,
            email=email,
            phone=phone,
            cover_letter=cover_letter,
            resume=resume
        )

        # Notifications
        Notification.objects.create(
            message=f"📩 New application from {name} for {job.title}",
            recipient=None
        )

        Notification.objects.create(
            message=f"✅ Your application for {job.title} has been submitted",
            recipient=user
        )

        AdminLog.objects.create(
            action=f"{name} applied for {job.title}"
        )

        return Response({"message": "Application submitted successfully"}, status=201)


# ================= ADMIN APPLICATION LIST =================
class AdminApplicationListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):

        applications = Application.objects.select_related(
            "job", "user"
        ).all().order_by("-applied_at")

        serializer = ApplicationSerializer(
            applications,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


# ================= ADMIN APPLICATION DETAIL =================
class AdminApplicationDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, id):

        application = get_object_or_404(
            Application.objects.select_related("job", "user"),
            id=id
        )

        serializer = ApplicationSerializer(
            application,
            context={"request": request}
        )

        return Response(serializer.data)


# ================= UPDATE APPLICATION STATUS =================
class UpdateApplicationStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, id):

        application = get_object_or_404(Application, id=id)

        status = request.data.get("status")
        admin_message = request.data.get("admin_message", "")

        application.status = status
        application.save()

        # Create notification for client
        message = f"📢 Your application for {application.job.title} is {status.upper()}."

        if admin_message:
            message += f" {admin_message}"

        Notification.objects.create(
            message=message,
            recipient=application.user
        )

        # Admin notification
        Notification.objects.create(
            message=f"Application status updated for {application.name} ({status.upper()})",
            recipient=None
        )

        AdminLog.objects.create(
            action=f"Admin changed status of {application.name} to {status}"
        )

        # Email notification
        try:
            send_mail(
                "Application Status Update",
                message,
                settings.EMAIL_HOST_USER,
                [application.email],
                fail_silently=True
            )
        except:
            pass

        return Response({"message": "Application status updated"})


# ================= CLIENT MY APPLICATIONS =================
class MyApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        applications = Application.objects.filter(
            user=request.user
        ).select_related("job").order_by("-applied_at")

        serializer = ApplicationSerializer(
            applications,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


# ================= CLIENT NOTIFICATIONS =================
class ClientNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by("-timestamp")[:50]

        serializer = NotificationSerializer(notifications, many=True)

        return Response(serializer.data)

    def patch(self, request, id):

        notification = get_object_or_404(
            Notification,
            id=id,
            recipient=request.user
        )

        notification.read = request.data.get("read", True)
        notification.save()

        return Response({"message": "Notification updated"})


# ================= ADMIN NOTIFICATIONS =================
class AdminNotificationsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):

        notifications = Notification.objects.filter(
            recipient__isnull=True
        ).order_by("-timestamp")[:50]

        serializer = NotificationSerializer(notifications, many=True)

        return Response(serializer.data)

    def patch(self, request, id):

        notification = get_object_or_404(
            Notification,
            id=id,
            recipient__isnull=True
        )

        notification.read = request.data.get("read", True)
        notification.save()

        return Response({"message": "Notification updated"})


# ================= ADMIN ACTIVITY LOGS =================
class AdminLogsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):

        logs = AdminLog.objects.all().order_by("-created_at")

        serializer = AdminLogSerializer(logs, many=True)

        return Response(serializer.data)