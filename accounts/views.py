from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()  # ✅ Use custom user model


# ================= CLIENT REGISTER =================
class ClientRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response(
                {"error": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create client user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="client"   # force client role
        )

        return Response(
            {"message": "Client registered successfully"},
            status=status.HTTP_201_CREATED
        )


# ================= CLIENT LOGIN =================
class ClientLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None or user.role != "client":
            return Response(
                {"error": "Invalid client credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "username": user.username,
            "role": user.role
        }, status=status.HTTP_200_OK)


# ================= CLIENT PROFILE =================
class ClientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "client":
            return Response(
                {"error": "Not a client account"},
                status=status.HTTP_403_FORBIDDEN
            )

        data = {
            "username": user.username,
            "email": user.email,
            "role": user.role
        }

        return Response(data, status=status.HTTP_200_OK)


# ================= ADMIN LOGIN =================
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid username or password ❌"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if admin
        if user.role != "admin":
            return Response(
                {"error": "Not an admin account ❌"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ Admin login success
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "username": user.username,
            "role": user.role
        }, status=status.HTTP_200_OK)