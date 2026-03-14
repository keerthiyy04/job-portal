# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()

# -------- CLIENT REGISTER ----------
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class ClientRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role="client"
        )
        return user
# -------- LOGIN ----------
from rest_framework import serializers
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data["username"],
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials ❌")

        return {"user": user}