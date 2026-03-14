from django.urls import path
from .views import (
    ClientJobListView,
    ApplyJobAPIView,
    AdminJobListView,
    AdminApplicationListView,
    AdminApplicationDetailView,
    UpdateApplicationStatusView,
    MyApplicationsView,
    AdminNotificationsView,
    ClientProfileAPIView,
    ClientNotificationsView,
    AdminLogsView,
)

urlpatterns = [
    # ======================================================
    # CLIENT JOBS
    # ======================================================
    # GET all jobs
    path("jobs/", ClientJobListView.as_view(), name="client-jobs"),
    # GET job details by ID
    path("jobs/<int:id>/", ClientJobListView.as_view(), name="client-job-detail"),
    # APPLY for job
    path("jobs/<int:job_id>/apply/", ApplyJobAPIView.as_view(), name="apply-job"),

    # ======================================================
    # CLIENT PROFILE
    # ======================================================
    # GET / UPDATE profile
    path("client/profile/", ClientProfileAPIView.as_view(), name="client-profile"),

    # ======================================================
    # CLIENT APPLICATIONS
    # ======================================================
    # GET logged-in user applications
    path("my-applications/", MyApplicationsView.as_view(), name="my-applications"),

    # ======================================================
    # CLIENT NOTIFICATIONS
    # ======================================================
    # GET all client notifications
    path("client/notifications/", ClientNotificationsView.as_view(), name="client-notifications"),
    # UPDATE client notification read status
    path(
        "client/notifications/<int:id>/",
        ClientNotificationsView.as_view(),
        name="update-client-notification",
    ),

    # ======================================================
    # ADMIN JOB MANAGEMENT
    # ======================================================
    # GET all jobs / CREATE job
    path("admin/jobs/", AdminJobListView.as_view(), name="admin-jobs"),
    # GET / UPDATE / DELETE job by ID
    path("admin/jobs/<int:id>/", AdminJobListView.as_view(), name="admin-job-detail"),

    # ======================================================
    # ADMIN APPLICATION MANAGEMENT
    # ======================================================
    # GET all applications
    path("admin/applications/", AdminApplicationListView.as_view(), name="admin-applications"),
    # GET application details by ID
    path(
        "admin/applications/<int:id>/",
        AdminApplicationDetailView.as_view(),
        name="admin-application-detail",
    ),
    # UPDATE application status
    path(
        "admin/applications/<int:id>/status/",
        UpdateApplicationStatusView.as_view(),
        name="update-application-status",
    ),

    # ======================================================
    # ADMIN NOTIFICATIONS
    # ======================================================
    # GET all admin notifications
    path("admin/notifications/", AdminNotificationsView.as_view(), name="admin-notifications"),
    # UPDATE admin notification read status
    path(
        "admin/notifications/<int:id>/",
        AdminNotificationsView.as_view(),
        name="update-admin-notification",
    ),

    # ======================================================
    # ADMIN ACTIVITY LOGS
    # ======================================================
    path("admin/logs/", AdminLogsView.as_view(), name="admin-logs"),
]