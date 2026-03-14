from django.urls import path
from .views import ClientRegisterView, ClientLoginView, AdminLoginView, ClientProfileView

urlpatterns = [
    path("client/register/", ClientRegisterView.as_view()),
    path("client/login/", ClientLoginView.as_view()),
    path("admin/login/", AdminLoginView.as_view()),

    # ✅ PROFILE
    path("client/profile/", ClientProfileView.as_view()),
]