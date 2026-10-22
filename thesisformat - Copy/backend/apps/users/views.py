
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="first_name", max_length=150)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("name", "email", "password")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Email sudah terdaftar."
            )
        return value

    def create(self, validated_data):
        email = validated_data["email"].strip().lower()

        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            first_name=validated_data["first_name"],
        )
        return user


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = self.initial_data.get("email", "").strip().lower()
        password = self.initial_data.get("password", "")

        user = User.objects.filter(email__iexact=email).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "Email atau password salah."}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "Akun tidak aktif."}
            )

        data = super().validate({
            "username": user.get_username(),
            "password": password,
        })

        data["user"] = {
            "id": user.pk,
            "name": user.first_name or user.get_username(),
            "email": user.email,
        }

        return data


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
