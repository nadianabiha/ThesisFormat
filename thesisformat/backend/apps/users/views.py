import re

from django.contrib.auth import get_user_model
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

# Username: 3–30 karakter, huruf/angka/titik/garis bawah, tanpa "@"
# (agar tidak tertukar dengan email saat login).
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.]{3,30}$")


def user_payload(user):
    """Data pengguna yang dikirim ke Flutter & Web Dashboard."""
    return {
        "id": str(user.pk),
        "name": user.get_full_name().strip() or user.username,
        "username": user.username,
        "email": user.email,
        # Dipakai Web Dashboard untuk menolak akun non-admin.
        "is_staff": user.is_staff,
    }


def clean_username(value, exclude_pk=None):
    username = value.strip().lower()
    if not USERNAME_RE.match(username):
        raise serializers.ValidationError(
            "Username 3–30 karakter, hanya huruf, angka, titik, atau garis bawah."
        )
    taken = User.objects.filter(username__iexact=username)
    if exclude_pk is not None:
        taken = taken.exclude(pk=exclude_pk)
    if taken.exists():
        raise serializers.ValidationError("Username ini sudah dipakai.")
    return username


def clean_email(value, exclude_pk=None):
    email = value.strip().lower()
    taken = User.objects.filter(email__iexact=email)
    if exclude_pk is not None:
        taken = taken.exclude(pk=exclude_pk)
    if taken.exists():
        raise serializers.ValidationError("Email ini sudah terdaftar.")
    return email


class RegisterSerializer(serializers.ModelSerializer):
    # Nama lengkap opsional (app tidak memintanya lagi); disimpan di first_name.
    name = serializers.CharField(
        source="first_name", max_length=150, required=False, allow_blank=True
    )
    # Opsional agar klien lama tetap jalan; jika kosong, username = email.
    username = serializers.CharField(max_length=30, required=False, allow_blank=True)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("id", "name", "username", "email", "password")
        read_only_fields = ("id",)

    def validate_email(self, value):
        return clean_email(value)

    def validate_username(self, value):
        return clean_username(value) if value.strip() else ""

    def create(self, validated_data):
        name = validated_data.pop("first_name", "").strip()
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        username = validated_data.pop("username", "") or email

        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name,
            **validated_data,
        )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ThesisFormatTokenSerializer(TokenObtainPairSerializer):
    """
    Login dengan username ATAU email (kolom "username" berisi salah satunya),
    lalu tambahkan data user pada respons token.
    """

    def validate(self, attrs):
        identifier = (attrs.get(self.username_field) or "").strip()
        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).order_by("pk").first()
        else:
            user = User.objects.filter(username__iexact=identifier).order_by("pk").first()
        if user is not None:
            attrs[self.username_field] = user.get_username()

        data = super().validate(attrs)
        data["user"] = user_payload(self.user)
        return data


class ThesisFormatTokenView(TokenObtainPairView):
    serializer_class = ThesisFormatTokenSerializer


class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="first_name", max_length=150)
    username = serializers.CharField(max_length=30)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ("id", "name", "username", "email")
        read_only_fields = ("id",)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Nama wajib diisi.")
        return value

    def validate_username(self, value):
        # Akun lama memakai email sebagai username; tetap boleh disimpan
        # selama tidak diubah.
        if value.strip().lower() == self.instance.username.lower():
            return self.instance.username
        return clean_username(value, exclude_pk=self.instance.pk)

    def validate_email(self, value):
        return clean_email(value, exclude_pk=self.instance.pk)

    def update(self, instance, validated_data):
        if "first_name" in validated_data:
            # Nama lengkap disimpan utuh di first_name.
            instance.last_name = ""
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return user_payload(instance)


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/users/me/ — lihat & ubah profil sendiri."""

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_current_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Password saat ini salah.")
        return value

    def validate(self, attrs):
        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "Password baru harus berbeda dari password saat ini."}
            )
        return attrs


class ChangePasswordView(APIView):
    """POST /api/users/me/password/ — ganti password sendiri."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password berhasil diubah."}, status=status.HTTP_200_OK)
