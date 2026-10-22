from django.contrib.auth import get_user_model
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    # Form Flutter mengirim "name"; nilainya disimpan di first_name.
    name = serializers.CharField(source="first_name", max_length=150)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("id", "name", "email", "password")
        read_only_fields = ("id",)

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("Email ini sudah terdaftar.")
        return normalized

    def create(self, validated_data):
        name = validated_data.pop("first_name").strip()
        email = validated_data.pop("email").strip().lower()
        password = validated_data.pop("password")

        # Endpoint JWT bawaan Django REST SimpleJWT menerima "username".
        # Agar pengguna bisa login dengan email, username dibuat sama dengan email.
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
            **validated_data,
        )
        return user


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ThesisFormatTokenSerializer(TokenObtainPairSerializer):
    """Tambahkan data user pada respons token untuk dipakai Flutter."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["user"] = {
            "id": str(user.pk),
            "name": user.get_full_name().strip() or user.username,
            "email": user.email,
        }
        return data


class ThesisFormatTokenView(TokenObtainPairView):
    serializer_class = ThesisFormatTokenSerializer
