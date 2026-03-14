# backend/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import ClientRegisterSerializer, LoginSerializer

# ================== CLIENT REGISTRATION ==================
class ClientRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClientRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # role is forced inside serializer
            return Response(
                {"message": "Client registered successfully ✅"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ================== CLIENT LOGIN ==================
class ClientLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            if user.role != "client":
                return Response(
                    {"error": "Invalid client credentials ❌"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user.role,
                "username": user.username
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ================== ADMIN LOGIN ==================
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            if user.role != "admin":
                return Response(
                    {"error": "Invalid admin credentials ❌"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user.role,
                "username": user.username
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)